# CAN Channel Backend Server with FastAPI
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from canlib import canlib, Frame
import logging
import threading
import time
from datetime import datetime
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="CAN Channel Backend API",
    description="A comprehensive REST API for CAN channel management, message sending, and real-time monitoring using Kvaser canlib",
    version="2.0",
    docs_url="/swagger",  # Swagger UI at /swagger
    redoc_url="/redoc"    # ReDoc at /redoc
)

# Enable CORS for web applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for monitoring
monitoring_active = False
monitoring_thread = None
received_messages = []
MAX_STORED_MESSAGES = 100

# Pydantic models for request/response validation
class Channel(BaseModel):
    channel_number: int = Field(..., description="Channel number")
    channel_name: str = Field(..., description="Channel name")
    product_number: str = Field(..., description="Product number")
    serial_number: int = Field(..., description="Serial number")
    local_channel_number: int = Field(..., description="Local channel number on device")
    full_description: str = Field(..., description="Full channel description")

class ChannelsResponse(BaseModel):
    status: str = Field(..., description="Response status")
    total_channels: int = Field(..., description="Total number of channels")
    channels: List[Channel] = Field(..., description="List of channels")

class SendMessageRequest(BaseModel):
    channel: int = Field(..., ge=0, le=3, description="CAN channel number (0-3)")
    can_id: int = Field(..., ge=0, le=2047, description="CAN message ID")
    dlc: int = Field(0, ge=0, le=8, description="Data Length Code (0-8)")
    data: Optional[List[int]] = Field(None, max_items=8, description="Data bytes (legacy format)")
    byte0: Optional[int] = Field(0, ge=0, le=255, description="Data byte 0")
    byte1: Optional[int] = Field(0, ge=0, le=255, description="Data byte 1")
    byte2: Optional[int] = Field(0, ge=0, le=255, description="Data byte 2")
    byte3: Optional[int] = Field(0, ge=0, le=255, description="Data byte 3")
    byte4: Optional[int] = Field(0, ge=0, le=255, description="Data byte 4")
    byte5: Optional[int] = Field(0, ge=0, le=255, description="Data byte 5")
    byte6: Optional[int] = Field(0, ge=0, le=255, description="Data byte 6")
    byte7: Optional[int] = Field(0, ge=0, le=255, description="Data byte 7")
    bitrate: Optional[int] = Field(250000, description="CAN bitrate (optional, default: 250000)")

    class Config:
        schema_extra = {
            "example": {
                "channel": 0,
                "can_id": 123,
                "dlc": 6,
                "byte0": 72,
                "byte1": 69,
                "byte2": 76,
                "byte3": 76,
                "byte4": 79,
                "byte5": 33,
                "byte6": 0,
                "byte7": 0,
                "bitrate": 250000
            }
        }


class MonitorStartRequest(BaseModel):
    channel: int = Field(..., ge=0, le=3, description="CAN channel number to monitor")
    duration: int = Field(30, ge=1, le=300, description="Monitoring duration in seconds")

    class Config:
        schema_extra = {
            "example": {
                "channel": 1,
                "duration": 30
            }
        }

class CANMessage(BaseModel):
    timestamp: str = Field(..., description="Message timestamp (ISO format)")
    channel: int = Field(..., description="Source channel")
    can_id: int = Field(..., description="CAN message ID")
    data: List[int] = Field(..., description="Message data bytes")
    dlc: int = Field(..., description="Data Length Code")
    flags: str = Field(..., description="Message flags")

class MessagesResponse(BaseModel):
    status: str = Field(..., description="Response status")
    total_messages: int = Field(..., description="Total number of messages")
    messages: List[CANMessage] = Field(..., description="List of CAN messages")

class StatusResponse(BaseModel):
    status: str = Field(..., description="Response status")
    message: Optional[str] = Field(None, description="Status message")

class MonitoringStatusResponse(BaseModel):
    status: str = Field(..., description="Response status")
    monitoring_active: bool = Field(..., description="Whether monitoring is active")
    stored_messages: int = Field(..., description="Number of stored messages")
    max_stored_messages: int = Field(..., description="Maximum number of stored messages")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")

# Helper functions
def get_channel_info():
    """Get information about all available CAN channels"""
    try:
        num_channels = canlib.getNumberOfChannels()
        channels = []
        
        for ch in range(num_channels):
            chd = canlib.ChannelData(ch)
            channel_info = Channel(
                channel_number=ch,
                channel_name=chd.channel_name,
                product_number=chd.card_upc_no.product(),
                serial_number=chd.card_serial_no,
                local_channel_number=chd.chan_no_on_card,
                full_description=f"{chd.channel_name} ({chd.card_upc_no.product()}:{chd.card_serial_no}/{chd.chan_no_on_card})"
            )
            channels.append(channel_info)
        
        return ChannelsResponse(
            status="success",
            total_channels=num_channels,
            channels=channels
        )
    except Exception as e:
        logger.error(f"Error getting channel info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def send_can_message(channel_id: int, can_id: int, data: List[int], bitrate: int = canlib.canBITRATE_250K):
    """Send a CAN message on the specified channel"""
    ch = None
    try:
        # Open channel
        ch = canlib.openChannel(channel=channel_id)
        
        # Set bus parameters based on Kvaser documentation
        if bitrate == 250000:
            ch.setBusParams(canlib.canBITRATE_250K)
        elif bitrate == 500000:
            ch.setBusParams(canlib.canBITRATE_500K)
        elif bitrate == 1000000:
            ch.setBusParams(canlib.canBITRATE_1M)
        else:
            ch.setBusParams(bitrate)
        
        # Set bus output control to normal (not silent)
        ch.setBusOutputControl(canlib.Driver.NORMAL)
        
        try:
            # Clear any pending transmit buffer using the proper method
            ch.iocontrol.flush_tx_buffer()
        except Exception as e:
            # If flush_tx_buffer fails, log and continue
            logger.warning(f"Couldn't flush TX buffer: {str(e)}")
        
        # Try to set up the channel for self-reception mode (helpful for testing)
        try:
            ch.iocontrol.local_txecho = True
        except Exception as e:
            logger.warning(f"Couldn't set local_txecho: {str(e)}")
            
        # Activate the CAN chip
        ch.busOn()
        
        # Wait for bus to stabilize
        time.sleep(0.1)
        
        # Create the frame
        frame = Frame(id_=can_id, data=data, flags=canlib.MessageFlag.STD)
        
        # Use writeWait instead of write to ensure message is sent
        # This will wait up to 500ms for acknowledgement
        ch.writeWait(frame, timeout=500)
        
        return StatusResponse(
            status="success",
            message=f"CAN message sent successfully on channel {channel_id}, ID {can_id}"
        )
    except canlib.CanNoMsg as e:
        logger.error(f"No CAN message available: {str(e)}")
        raise HTTPException(status_code=500, detail=f"No CAN message available: {str(e)}")
    except canlib.CanTimeout as e:
        logger.error(f"Timeout sending CAN message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Timeout sending CAN message. This often happens when no other device is connected to acknowledge the message.")
    except canlib.CanError as e:
        logger.error(f"CAN error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CAN error: {str(e)}")
    except Exception as e:
        logger.error(f"Error sending CAN message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up
        if ch is not None:
            try:
                ch.busOff()
                ch.close()
            except Exception as e:
                logger.error(f"Error closing channel: {str(e)}")

def monitor_can_messages(channel_id: int, duration: int = 10):
    """Monitor CAN messages on a specific channel"""
    global received_messages, monitoring_active
    
    ch = None
    try:
        # Open channel
        ch = canlib.openChannel(channel=channel_id)
        
        # Set up the channel properly with more configuration options
        ch.setBusParams(canlib.canBITRATE_250K)
        ch.setBusOutputControl(canlib.Driver.NORMAL)
        
        # Configure acceptance filter to accept all messages (standard frames)
        ch.acceptance_filter(accept_code=0, accept_mask=0, format=canlib.MessageFlag.STD)
        
        # For handling error frames, set standard flags
        ch.setBusOutputControl(canlib.Driver.NORMAL)
        
        # Activate the CAN chip
        ch.busOn()
        
        start_time = time.time()
        monitoring_active = True
        
        logger.info(f"Starting CAN monitoring on channel {channel_id} for {duration} seconds")
        
        while monitoring_active and (time.time() - start_time) < duration:
            try:
                # Try to read a message with a short timeout
                msg = ch.read(timeout=100)  # 100ms timeout for more responsive reading
                
                # Skip error frames in the stored messages but log them
                if canlib.MessageFlag.ERROR_FRAME in msg.flags:
                    logger.warning(f"Error frame received: ID={msg.id}, Flags={msg.flags}")
                    continue
                
                message_data = CANMessage(
                    timestamp=datetime.now().isoformat(),
                    channel=channel_id,
                    can_id=msg.id,
                    data=list(msg.data),
                    dlc=msg.dlc,
                    flags=str(msg.flags)
                )
                
                received_messages.append(message_data)
                
                # Keep only the last MAX_STORED_MESSAGES messages
                if len(received_messages) > MAX_STORED_MESSAGES:
                    received_messages.pop(0)
                    
                logger.info(f"Received message: ID={msg.id}, Data={list(msg.data)}")
                
            except canlib.CanNoMsg:
                # No message received, continue monitoring
                continue
            except canlib.CanError as e:
                logger.error(f"CAN error during monitoring: {str(e)}")
                time.sleep(0.1)  # Small delay to prevent CPU overload on repeated errors
                continue
            except Exception as e:
                logger.error(f"Error reading CAN message: {str(e)}")
                time.sleep(0.1)  # Small delay to prevent CPU overload on repeated errors
                continue
        
    except Exception as e:
        logger.error(f"Error in CAN monitoring: {str(e)}")
    finally:
        # Clean up
        if ch is not None:
            try:
                ch.busOff()
                ch.close()
            except Exception as e:
                logger.error(f"Error closing channel: {str(e)}")
        
        monitoring_active = False
        logger.info(f"CAN monitoring stopped on channel {channel_id}")

def start_monitoring_thread(channel_id: int, duration: int):
    """Start monitoring in a separate thread"""
    global monitoring_thread, monitoring_active
    
    if monitoring_active:
        raise HTTPException(status_code=400, detail="Monitoring is already active")
    
    # Clear any previous messages
    global received_messages
    received_messages = []
    
    monitoring_thread = threading.Thread(target=monitor_can_messages, args=(channel_id, duration))
    monitoring_thread.daemon = True
    monitoring_thread.start()
    
    return StatusResponse(
        status="success",
        message=f"Started monitoring channel {channel_id} for {duration} seconds"
    )

# API Routes

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home():
    """Home page with navigation"""
    return """
    <html>
    <head>
        <title>CAN Channel Backend API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .container { text-align: center; }
            .btn { display: inline-block; padding: 15px 30px; margin: 10px; text-decoration: none; 
                   border-radius: 5px; font-weight: bold; transition: all 0.3s; }
            .btn-primary { background-color: #007bff; color: white; }
            .btn-primary:hover { background-color: #0056b3; }
            .btn-secondary { background-color: #6c757d; color: white; }
            .btn-secondary:hover { background-color: #545b62; }
            .features { text-align: left; margin: 30px 0; }
            .features li { margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚗 CAN Channel Backend API (FastAPI)</h1>
            <p>Interactive API documentation and testing interface</p>
            
            <div>
                <a href="/swagger" class="btn btn-primary">📚 Open Swagger UI</a>
                <a href="/redoc" class="btn btn-secondary">📖 Open ReDoc</a>
                <a href="/channels" class="btn btn-secondary">🔍 Test API</a>
            </div>
            
            <div class="features">
                <h3>Available Features:</h3>
                <ul>
                    <li>🔍 <strong>Channel Discovery</strong> - Detect and list CAN channels</li>
                    <li>📤 <strong>Message Sending</strong> - Send CAN messages with validation</li>
                    <li>📥 <strong>Real-time Monitoring</strong> - Monitor incoming messages</li>
                    <li>📊 <strong>Message History</strong> - Store and retrieve messages</li>
                    <li>📖 <strong>Interactive Documentation</strong> - Swagger UI and ReDoc</li>
                    <li>🌐 <strong>CORS Support</strong> - Ready for web applications</li>
                    <li>⚡ <strong>FastAPI Performance</strong> - High performance async API</li>
                </ul>
            </div>
            
            <div>
                <h3>Quick Links:</h3>
                <p><strong>Swagger UI:</strong> <a href="/swagger">/swagger</a></p>
                <p><strong>ReDoc:</strong> <a href="/redoc">/redoc</a></p>
                <p><strong>Channels API:</strong> <a href="/channels">/channels</a></p>
                <p><strong>Health Check:</strong> <a href="/health">/health</a></p>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="CAN Channel Server with FastAPI",
        version="2.0",
        timestamp=datetime.now().isoformat()
    )

@app.get("/channels", response_model=ChannelsResponse, tags=["Channels"])
async def get_channels():
    """Get all available CAN channels"""
    return get_channel_info()

@app.get("/channels/{channel_id}", response_model=Channel, tags=["Channels"])
async def get_channel(channel_id: int):
    """Get information about a specific CAN channel"""
    try:
        num_channels = canlib.getNumberOfChannels()
        
        if channel_id < 0 or channel_id >= num_channels:
            raise HTTPException(
                status_code=404, 
                detail=f"Channel {channel_id} not found. Available channels: 0-{num_channels-1}"
            )
        
        chd = canlib.ChannelData(channel_id)
        return Channel(
            channel_number=channel_id,
            channel_name=chd.channel_name,
            product_number=chd.card_upc_no.product(),
            serial_number=chd.card_serial_no,
            local_channel_number=chd.chan_no_on_card,
            full_description=f"{chd.channel_name} ({chd.card_upc_no.product()}:{chd.card_serial_no}/{chd.chan_no_on_card})"
        )
    except Exception as e:
        logger.error(f"Error getting channel {channel_id} info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/messages/send", response_model=StatusResponse, tags=["Messages"])
async def send_message(request: SendMessageRequest):
    """Send a CAN message"""
    try:
        # Validate channel exists
        num_channels = canlib.getNumberOfChannels()
        if request.channel < 0 or request.channel >= num_channels:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid channel {request.channel}. Available channels: 0-{num_channels-1}"
            )
        
        # Determine which data format to use
        data = []
        
        # Check if we should use the data array or individual bytes
        if request.data is not None and len(request.data) >= request.dlc:
            # Legacy format - use the data array if it has enough bytes
            data = request.data[:request.dlc]  # Take only up to dlc bytes
            # Validate data bytes
            for byte_val in data:
                if byte_val < 0 or byte_val > 255:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Invalid byte value {byte_val}. Must be 0-255"
                    )
        else:
            # Use individual byte fields
            data = [
                request.byte0, request.byte1, request.byte2, request.byte3,
                request.byte4, request.byte5, request.byte6, request.byte7
            ][:request.dlc]  # Take only the number of bytes specified in dlc
            
        # Ensure the data length matches the DLC
        if len(data) < request.dlc:
            # Pad with zeros if not enough data
            data.extend([0] * (request.dlc - len(data)))
        
        logger.info(f"Sending CAN message with ID={request.can_id}, DLC={request.dlc}, data={data}")
        
        return send_can_message(request.channel, request.can_id, data, request.bitrate)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in send_message endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/monitoring/start", response_model=StatusResponse, tags=["Monitoring"])
async def start_monitoring(request: MonitorStartRequest):
    """Start CAN message monitoring"""
    try:
        # Validate channel exists
        num_channels = canlib.getNumberOfChannels()
        if request.channel < 0 or request.channel >= num_channels:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid channel {request.channel}. Available channels: 0-{num_channels-1}"
            )
        
        return start_monitoring_thread(request.channel, request.duration)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in start_monitoring endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/monitoring/stop", response_model=StatusResponse, tags=["Monitoring"])
async def stop_monitoring():
    """Stop CAN message monitoring"""
    global monitoring_active
    
    if monitoring_active:
        monitoring_active = False
        return StatusResponse(
            status="success",
            message="Monitoring stopped"
        )
    else:
        return StatusResponse(
            status="info",
            message="Monitoring was not active"
        )

@app.get("/monitoring/messages", response_model=MessagesResponse, tags=["Monitoring"])
async def get_messages():
    """Get received CAN messages"""
    return MessagesResponse(
        status="success",
        total_messages=len(received_messages),
        messages=received_messages
    )

@app.get("/monitoring/status", response_model=MonitoringStatusResponse, tags=["Monitoring"])
async def get_monitoring_status():
    """Get current monitoring status"""
    return MonitoringStatusResponse(
        status="success",
        monitoring_active=monitoring_active,
        stored_messages=len(received_messages),
        max_stored_messages=MAX_STORED_MESSAGES
    )

@app.get("/troubleshoot", response_model=StatusResponse, tags=["System"])
async def troubleshoot_can_bus():
    """Run diagnostics on the CAN bus and channels"""
    try:
        # Get channel information
        num_channels = canlib.getNumberOfChannels()
        if num_channels == 0:
            return StatusResponse(
                status="error",
                message="No CAN channels found. Make sure your Kvaser device is properly connected."
            )
        
        # Check channel status
        channel_statuses = []
        for ch_idx in range(num_channels):
            try:
                # Try to open each channel
                ch = canlib.openChannel(ch_idx)
                
                # Get channel data
                chd = canlib.ChannelData(ch_idx)
                
                # Try to go on bus briefly
                try:
                    ch.setBusParams(canlib.canBITRATE_250K)
                    ch.setBusOutputControl(canlib.Driver.NORMAL)
                    ch.busOn()
                    time.sleep(0.1)
                    bus_status = "OK"
                except canlib.CanError as e:
                    bus_status = f"Error: {str(e)}"
                finally:
                    ch.busOff()
                
                channel_statuses.append(f"Channel {ch_idx}: {chd.channel_name} - Bus status: {bus_status}")
                ch.close()
            except canlib.CanError as e:
                channel_statuses.append(f"Channel {ch_idx}: Error accessing - {str(e)}")
        
        # Common troubleshooting tips
        tips = [
            "- Blinking red light indicates error frames - make sure at least two channels are connected and on bus",
            "- Check that bitrates are the same on all channels",
            "- Ensure proper termination (60 Ohm) on the CAN bus",
            "- Make sure that the transmitting channel is in NORMAL mode, not SILENT",
            "- If messages are failing, try going off and then on bus to clear the transmit buffer"
        ]
        
        return StatusResponse(
            status="success",
            message=f"Found {num_channels} CAN channels.\n\nChannel status:\n" + 
                     "\n".join(channel_statuses) + 
                     "\n\nTroubleshooting tips:\n" + 
                     "\n".join(tips)
        )
    except Exception as e:
        logger.error(f"Error in troubleshoot endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    logger.info("Starting CAN Channel Backend Server with FastAPI...")
    logger.info("Available endpoints:")
    logger.info("  Swagger UI:    http://localhost:8000/swagger")
    logger.info("  ReDoc:         http://localhost:8000/redoc")
    logger.info("  Home:          http://localhost:8000/")
    logger.info("  Health:        http://localhost:8000/health")
    logger.info("  Channels:      http://localhost:8000/channels")
    logger.info("  Send Message:  http://localhost:8000/messages/send")
    logger.info("  Monitoring:    http://localhost:8000/monitoring/")
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
