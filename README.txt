TvServer
========

A REST-based interface for HDHomeRun and Video4Linux DVB TV tuners.

This is currently a work-in-progress. Though TV tuners can be controlled, I am still debugging the GStreamer integration.

Remaining Tasks
---------------

X Debug DVB capture. MPEG-TS stream was missing PMT packets due to a basic 
  design/documentation flaw of dvb-apps' azap tool (which "zaplib" and "pyzap"
  are modeled after).
  X "zaplib" and "pyzap" updated.
X Finish streaming of local DVB devices.
X GStreamer pipeline for RTP/H264 feed from HDHR figured-out.
X GStreamer pipeline for local MPEGTS feed figured-out.
> Finish GStreamer implementation.
> Finish README.

