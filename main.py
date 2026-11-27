#!/usr/bin/env python3
"""Sum up 26 November 2026's world news in one image.

Entry for make.fun bounty news-image-20261126.

The program draws a 1024x1024 newspaper front page with Python's standard
library only (no network, no external files, no installed packages) and
writes it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png outside
the grader). Every run produces byte-identical output: fixed layout, fixed
text, fixed colours, and zlib level 9 with no timestamps anywhere.

How the picture is drawn
-------------------------
* A small RGB canvas with rectangle / circle / polygon / line primitives.
* Text from a bitmap font baked into this file as one base64 blob
  (FONT_B64): Liberation Sans Bold rasterised once at 28 px, 2 bits per
  pixel, so the program needs no font files at run time. The blob is data,
  the drawing and layout code around it is the program.
* A deterministic PNG writer (zlib, filter 0, fixed chunk order).

The news on the page (all first reported on Thursday 26 November 2026,
checked against Reuters / CNN / WSJ / Daily Summary of World):
* Strait of Hormuz: Iran's Revolutionary Guards say two oil tankers hit
  sea mines off Oman's Khasab port and caught fire; one was a supertanker
  carrying more than 2 million barrels of crude. The claim was not
  independently verified.
* Thanksgiving storm: the 100th Macy's Thanksgiving Day Parade in New
  York postponed to Saturday, a first; the storm cut power to about
  900,000 homes and businesses.
* Spain: snap general election on Sunday 29 November; EU leaders pick
  Pablo Hernandez de Cos as the next ECB president (succeeds Lagarde
  in February 2027).
* Ukraine: Russian strikes kill at least three in Kharkiv; Kyiv warns
  of a new mass strike.
* Gaza: Qatar and Egypt meet in Cairo to push the Gaza truce forward.
* Microsoft outage enters its second day in 70+ countries: Outlook
  and Teams still down; hospitals and schools hit.
* Canary Islands: a record 2,100+ migrants arrive in one day.
* Mumbai marks 18 years since the 26/11 attacks of 2008.
* Also: Guinea-Bissau's vote delayed to 2028; a projectile hits the
  Jazan refinery in Saudi Arabia, killing one worker; NATO watches
  Polish airspace; Tidal drops AI-made tracks.
"""

import base64
import json
import os
import struct
import sys
import zlib
from pathlib import Path

# ---------------------------------------------------------------- font data
# One base64 blob: {"size": 28, "glyphs": [{"c", "w", "h", "top", "adv",
# "px" (base64 of 2-bit-packed pixels)}]}. Injected at build time from
# /tmp/font_blob.txt (see README); the program only decodes it.
FONT_B64 = "eyJzaXplIjoyOCwiZ2x5cGhzIjpbeyJjIjoiICIsInciOjAsImgiOjAsInRvcCI6MCwiYWR2Ijo4LCJweCI6IiJ9LHsiYyI6IiEiLCJ3Ijo1LCJoIjoxOSwidG9wIjotMTksImFkdiI6OSwicHgiOiJmNS9uK2Y1L24rUDQvVDlQMC9UOVAwQUFBZjUvbitmNCJ9LHsiYyI6IlwiIiwidyI6MTEsImgiOjcsInRvcCI6LTE5LCJhZHYiOjEzLCJweCI6IlA0ZjAvaC9UK0g5UDBQMC9RL1Q5RDhQMFB3QT0ifSx7ImMiOiIjIiwidyI6MTYsImgiOjE5LCJ0b3AiOi0xOSwiYWR2IjoxNiwicHgiOiJBQzRCOEFBOUF1QUFQQUxnQUh3RDBBQzRBOEEvLy8vOFAvLy8vQUR3RDBBQjhBOEFBdUFQQUFMZ0h3QUQwQzRBdi8vLzlMLy8vL1FMZ0h3QUMwQjRBQTlBdUFBZkFQUUFIZ0R3QUE9PSJ9LHsiYyI6IiQiLCJ3IjoxNiwiaCI6MjQsInRvcCI6LTIxLCJhZHYiOjE2LCJweCI6IkFBS0FBQUFEZ0FBQnYvNEFDLy8vMEIvLy8vQS8wNHYwUDRPRDVEK0RnQUEvMDRBQUgvK1FBQXYvL2dBQy8vL1FBQnYvOUFBRG0vd0FBNEw4YndPQi9IOURndncvMDRmOEwvLy85QXYvLzlBQnYvb0FBQU9BQUFBRGdBQUFBVUFBIn0seyJjIjoiJSIsInciOjI1LCJoIjoxOSwidG9wIjotMTksImFkdiI6MjUsInB4IjoiQXY1QUFEOEFBLy8wQUM5QUF2bS9BQitBQVB3UHdBL0FBSDRDOUF2UUFCK0F2UWZnQUFmZ0wwUHdBQUg0QzlMMXY0QS9BL0g1Ly93TDV2ajgvVytBLy95OWZnUHdDL2grSDREOEFBQS9DK0EvQUFBdlF2Z1B3QUFmZ0g0RDhBQVB3QitBL0FBTDBBUDV2Z0FINEFCLy93QUQ4QUFHL2dBPSJ9LHsiYyI6IiYiLCJ3IjoxOSwiaCI6MTksInRvcCI6LTE5LCJhZHYiOjIwLCJweCI6IkFBditBQUFCLy84QUFBLzEvZ0FBUHdIOEFBRDhCL0FBQS9BL2dBQVA2L2dBQUIvL2dBQUIvK0FBQUMvL0FEa0MvLzRDK0IvaC9RL1F2d0w4ZndQOEEvLzBDL0FILzhBdjRBditRRC82Ly8vMGYvLzYvOUFyL2tHL1FBPT0ifSx7ImMiOiInIiwidyI6NSwiaCI6NywidG9wIjotMTksImFkdiI6NywicHgiOiJ2Mi9IOGZ4L0g4ZncifSx7ImMiOiIoIiwidyI6OSwiaCI6MjYsInRvcCI6LTIwLCJhZHYiOjksInB4IjoiQVA4QXYwQS93Qy9RRC9BTDlBTDhBUDhBZjRBZjRBdjBBdjBBdjBBdjBBdjBBdjBBZjRBZjRBUDhBTDhBSDlBRC9BQy9RQS93QXYwQVA4QT0ifSx7ImMiOiIpIiwidyI6OCwiaCI6MjYsInRvcCI6LTIwLCJhZHYiOjksInB4IjoidjBBL3dDL1FEL0FMOUFQOEEvd0MvUUgrQVA0QS93RC9BUDhBL3dEL0FQOEEvZ0grQXYwRC9BUDRDL1FQOEMvUVA4Qy9RQT09In0seyJjIjoiKiIsInciOjExLCJoIjoxMCwidG9wIjotMTksImFkdiI6MTEsInB4IjoiQVB3QUEvQUNEOEl2djcyLy8vZ2YvUUIvOUFmMzlDOUg0QmdKQUE9PSJ9LHsiYyI6IisiLCJ3IjoxNSwiaCI6MTUsInRvcCI6LTE3LCJhZHYiOjE2LCJweCI6IkFCcEFBQUIrQUFBQitBQUFCK0FBQUIrQUFBQitBQS8vLy85Ly8vLzkvLy8vOUFCK0FBQUIrQUFBQitBQUFCK0FBQUIrQUFBQnFBQUEifSx7ImMiOiIsIiwidyI6NSwiaCI6OCwidG9wIjotNCwiYWR2Ijo4LCJweCI6IlA4L3ovUDhId3VEMHZBPT0ifSx7ImMiOiItIiwidyI6OCwiaCI6NCwidG9wIjotOSwiYWR2Ijo5LCJweCI6Ii8vMy8vZi85VlZRPSJ9LHsiYyI6Ii4iLCJ3Ijo1LCJoIjo0LCJ0b3AiOi00LCJhZHYiOjgsInB4IjoiUDgvei9QOD0ifSx7ImMiOiIvIiwidyI6OCwiaCI6MjEsInRvcCI6LTIwLCJhZHYiOjgsInB4IjoiQVAwQS9RSDhBZndDK0FQNEEvUUg4QWZ3QytBTDRBL1FEOUFmd0MvQUw0QS9nRDlBZndDL0FMNEEifSx7ImMiOiIwIiwidyI6MTQsImgiOjE5LCJ0b3AiOi0xOSwiYWR2IjoxNiwicHgiOiJBYi9nQUwvL3dCLy8vd1A5Qy9SL2dEL0w5QVA4dndBdjMvQUMvZjhBTDkvd0F2My9BQy9mOEFMOXZ3QXYyL1FEL0grQVA0UDlDL1FmLy84QXYvL0FBYi9nQUE9PSJ9LHsiYyI6IjEiLCJ3IjoxNCwiaCI6MTksInRvcCI6LTE5LCJhZHYiOjE2LCJweCI6IkFIL1FBQy85QUIvLzBBUCsvUUErTDlBQ0F2MEFBQy9RQUFMOUFBQXYwQUFDL1FBQUw5QUFBdjBBQUMvUUFBTDlBQUF2MEFBQy9RQi8vLy9uLy8vL2YvLy84QT09In0seyJjIjoiMiIsInciOjE1LCJoIjoxOSwidG9wIjotMTksImFkdiI6MTYsInB4IjoiQUcvNUFBLy8vZ0MvLy8wSC9SdjhMK0FQOEw4QVA4QUFBUDhBQUF2NEFBQy93QUFML1FBQS85QUFILzBBQWYrQUFBLzRBQUQvZ0FBTC9WVlVQLy8vK1AvLy8rUC8vLytBIn0seyJjIjoiMyIsInciOjE1LCJoIjoxOSwidG9wIjotMTksImFkdiI6MTYsInB4IjoiQUcvNUFBLy8vZ0QvLy8wSC9SLzhQOUFQOEw4QVA4QUFBUDhBQUIvMEFCLy9RQUIvNUFBQi8vd0FBRnY4QUFBTDliNEFIK1A4QUwrUC9WdjlILy8vOEIvLy93QUwvNUFBIn0seyJjIjoiNCIsInciOjE2LCJoIjoxOSwidG9wIjotMTksImFkdiI6MTYsInB4IjoiQUFEL3dBQUMvOEFBQi8vQUFBLy93QUF2djhBQWZ6L0FBUDAvd0FMNFA4QUg4RC9BRDlBL3dDK0FQOEIvQUQvQXYvLy8vYi8vLy8yLy8vLzlBQUEvd0FBQVA4QUFBRC9BQUFBL3dBPT0ifSx7ImMiOiI1IiwidyI6MTUsImgiOjE5LCJ0b3AiOi0xOSwiYWR2IjoxNiwicHgiOiJELy8vNEQvLy80RC8vLzREK0FBQUgrQUFBSDlBQUFIOXY5QUgvLy93TC8vLzRML1J2OUZVQUwrQUFBSCtBQUFIL0w4QUgrUDlBTCtML1J2OEQvLy80QS8vL2dBRy81QUEifSx7ImMiOiI2IiwidyI6MTQsImgiOjE5LCJ0b3AiOi0xOSwiYWR2IjoxNiwicHgiOiJBTC9rQUgvLzRBLy8vMEwrQy9nL2dENkw5QUFBdndBQUQvSC9nUCsvL3cvLy8vai8wSC9mOUFMKy93QWY2L1FCL24rQUw5UCtDL3dmLy8rQWYvL2dBTC9rQUE9PSJ9LHsiYyI6IjciLCJ3IjoxNCwiaCI6MTksInRvcCI6LTE5LCJhZHYiOjE2LCJweCI6Ii8vLy8zLy8vL2YvLy85RlZWdndBQUgrQUFBL3dBQUw5QUFBL2dBQUw4QUFCL2dBQVA4QUFCL2dBQUw5QUFBL3dBQUgrQUFBdjBBQUQvUUFBUDhBQUEvd0FBQT09In0seyJjIjoiOCIsInciOjE1LCJoIjoxOSwidG9wIjotMTksImFkdiI6MTYsInB4IjoiQUwvNUFCLy8vZ0QvNy80SC9BZjhMOUFQOUw5QVA5SCtBUDhEL1F2NEEvLy9nQWIvK0FDLzcvMEwrQVA5UDhBSCtQOEFIK1A4QUwrUCtBUDlILy8vOEIvLy93QUwvNUFBIn0seyJjIjoiOSIsInciOjE1LCJoIjoxOSwidG9wIjotMTksImFkdiI6MTYsInB4IjoiQUwvNEFCLy8vUUQvLy93TC9SLzRQOUFQOFA4QUw5UDhBTDlQOUFQK0wvQXYrSC8vLytCLy83K0FiK1g5QUFBTDlBQUFQOEc4QWY0SC9SLzBELy8vZ0IvLytBQUwva0FBIn0seyJjIjoiOiIsInciOjUsImgiOjE1LCJ0b3AiOi0xNSwiYWR2Ijo5LCJweCI6ImY1L24rZjRBQUFBQUFBQUFBQUgrZjUvbitBPT0ifSx7ImMiOiI7IiwidyI6NSwiaCI6MTksInRvcCI6LTE1LCJhZHYiOjksInB4IjoiZjUvbitmNEFBQUFBQUFBQUFBSCtmNS9uK0M0UFI4UGcifSx7ImMiOiI8IiwidyI6MTUsImgiOjE1LCJ0b3AiOi0xNywiYWR2IjoxNiwicHgiOiJBQUFBWkFBQWI5QUFMLzlBRy8vMEcvLzVBdi81QUEvK0FBQS9nQUFBLytBQUF2LzVBQUcvLzVBQUcvLzBBQUwvOUFBQWI5QUFBQVpBIn0seyJjIjoiPSIsInciOjE1LCJoIjoxMCwidG9wIjotMTQsImFkdiI6MTYsInB4IjoiLy8vLzkvLy8vOS8vLy85QUFBQUFBQUFBQUFBQUFBQUFBQUEvLy8vOS8vLy85Ly8vLzlBPSJ9LHsiYyI6Ij4iLCJ3IjoxNSwiaCI6MTUsInRvcCI6LTE3LCJhZHYiOjE2LCJweCI6Im9BQUFBLzBBQUEvL2tBQWIvL2dBQWYvK1FBQnYvOUFBQnY5QUFBSDlBQUJ2OUFCdi85QWYvK1FiLy9nQS8va0FBLzBBQUFvQUFBQUEifSx7ImMiOiI/IiwidyI6MTUsImgiOjE5LCJ0b3AiOi0xOSwiYWR2IjoxNywicHgiOiJBTC81QUIvLy9nSC8vLzRQL1J2OWY4QUw5djBBSCtBQUFMOUFBQXY4QUFDL3dBQWYrQUFBLzBBQUMvUUFBRC9BQUFBQUFBQUFBQUFBRC9BQUFEL0FBQUQvQUFBRC9BQUEifSx7ImMiOiJAIiwidyI6MjUsImgiOjIzLCJ0b3AiOi0xOSwiYWR2IjoyNywicHgiOiJBQUFiLytRQUFBQy8vLy9RQUFIK1FBYitBQUw0QUFBTDRBTDBBQUFBZlFIMEF2NVBTOEQ0QS8vM3dQUjhBL1FmOEM0dUF2QUMrQXVQUVBRQWZRSG53THdBSHdDNThDNEFDOEF1ZkErQUErQVBYd1BnQWZnSHg4QzhBUDBEMFBRZmdmdUg4RDRELy9YLzhBZlFMK0F2MEFEOEFBQUFBQUFmMEFBQUxBQUIvMUFHLzBBQUMvLy8vZ0FBQUJ2L3BBQUEifSx7ImMiOiJBIiwidyI6MjAsImgiOjE5LCJ0b3AiOi0xOSwiYWR2IjoyMCwicHgiOiJBQUwvZ0FBQUEvL0FBQUFILzlBQUFBdjc4QUFBRCtmd0FBQWYwL2dBQUMvQy9BQUFQNEg5QUFCL1FQNEFBUDhBdndBQi9nQi9RQUwvLy8rQUEvLy8vOEFILy8vLzRBdjBBQS93RC9BQUMvUWY0QUFIK0QvUUFBUDhQOEFBQXYwPSJ9LHsiYyI6IkIiLCJ3IjoxOCwiaCI6MTksInRvcCI6LTE5LCJhZHYiOjIwLCJweCI6IlAvLy9vQVAvLy8vUVAvLy8vMFA4QUIvNFA4QUF2OFA4QUFmOFA4QUF2NFA4QUIvd1AvLy8vUVAvLy85QVAvLy8vMFA4QUF2OVA4QUFIL1A4QUFEL1A4QUFIL1A4QUFmK1AvLy8vOFAvLy8vMFAvLy81QUE9In0seyJjIjoiQyIsInciOjE5LCJoIjoxOSwidG9wIjotMTksImFkdiI6MjAsInB4IjoiQUJ2L29BQUgvLy80QUgvLy8vZ0gvNVYvOUQvd0FDL3gvd0FBTGt2NEFBQUFMOUFBQUFEL1FBQUFBLzBBQUFBUDlBQUFBQy9RQUFBQXY0QUFBQUgvUUFBZVF2OEFBZjlELzVWditBZi8vLy9BQi8vLytBQUJ2L29BQUE9PSJ9LHsiYyI6IkQiLCJ3IjoxOSwiaCI6MTksInRvcCI6LTE5LCJhZHYiOjIwLCJweCI6IlAvLytRQUQvLy8vUUEvLy8vOUFQOEJiLzBEL0FBUC9BL3dBQS8wUDhBQUwrRC9BQUIvdy93QUFQOFA4QUFEL0QvQUFBL3cvd0FBZjhQOEFBTCtEL0FBRC9RL3dBRC93UDhBYi8wRC8vLy8wQS8vLy8wQVAvLytRQUFBPT0ifSx7ImMiOiJFIiwidyI6MTcsImgiOjE5LCJ0b3AiOi0xOSwiYWR2IjoxOSwicHgiOiJQLy8vL3cvLy8vL0QvLy8vOFA4QUFBQS93QUFBRC9BQUFBUDhBQUFBL3dBQUFELy8vLzBQLy8vL1EvLy8vOUQvQUFBQVA4QUFBQS93QUFBRC9BQUFBUDhBQUFBLy8vLy9qLy8vLytQLy8vLzQifSx7ImMiOiJGIiwidyI6MTYsImgiOjE5LCJ0b3AiOi0xOSwiYWR2IjoxNywicHgiOiJQLy8vL0QvLy8vdy8vLy84UDhBQUFEL0FBQUEvd0FBQVA4QUFBRC9BQUFBLy8vLzhQLy8vL0QvLy8vdy93QUFBUDhBQUFEL0FBQUEvd0FBQVA4QUFBRC9BQUFBL3dBQUFQOEFBQUE9PSJ9LHsiYyI6IkciLCJ3IjoyMCwiaCI6MTksInRvcCI6LTE5LCJhZHYiOjIyLCJweCI6IkFCdi81QUFCLy8vL1FBZi8vLy9RSC81VnYvQS85QUFmK0gvUUFBZVF2NEFBQUFDL1FBQUFBUDlBQUFBQS8wQUgvL3ovUUFmLy9MK0FCLy84djRBQUF2eC8wQUFDL0MvMEFBUDhILzVWci93SC8vLy85QUgvLy8rQUFCdi81QUE9In0seyJjIjoiSCIsInciOjE4LCJoIjoxOSwidG9wIjotMTksImFkdiI6MjAsInB4IjoiUDhBQUw5UDhBQUw5UDhBQUw5UDhBQUw5UDhBQUw5UDhBQUw5UDhBQUw5UDhBQUw5UC8vLy85UC8vLy85UC8vLy85UDlWVmY5UDhBQUw5UDhBQUw5UDhBQUw5UDhBQUw5UDhBQUw5UDhBQUw5UDhBQUw5QT0ifSx7ImMiOiJJIiwidyI6NSwiaCI6MTksInRvcCI6LTE5LCJhZHYiOjgsInB4IjoiUDgvei9QOC96L1A4L3ovUDgvei9QOC96L1A4L3ovUDgifSx7ImMiOiJKIiwidyI6MTQsImgiOjE5LCJ0b3AiOi0xOSwiYWR2IjoxNiwicHgiOiJBQi8vNEFILy9nQWYvK0FBVnY0QUFCL2dBQUgrQUFBZjRBQUIvZ0FBSCtBQUFmNEFBQi9nQUFIK0FBQWY1cmdDL24vQUwrUC9XLzB2Ly8rQXYvL2dBYi9rQUE9PSJ9LHsiYyI6IksiLCJ3IjoxOSwiaCI6MTksInRvcCI6LTE5LCJhZHYiOjIwLCJweCI6IlA4QUFQK0QvQUFQK0Evd0FQK0FQOEFQK0FEL0FQK0FBL3dQK0FBUDhQK0FBRC9QK0FBQS8vL2dBQVAvLzlBQUQvKy93QUEvNEwvQUFQOEEvNEFEL0FIL2dBL3dBZjlBUDhBQy8wRC9BQVAvQS93QUEvNFA4QUFIL2dBPT0ifSx7ImMiOiJMIiwidyI6MTYsImgiOjE5LCJ0b3AiOi0xOSwiYWR2IjoxNywicHgiOiJQOEFBQUQvQUFBQS93QUFBUDhBQUFEL0FBQUEvd0FBQVA4QUFBRC9BQUFBL3dBQUFQOEFBQUQvQUFBQS93QUFBUDhBQUFEL0FBQUEvd0FBQVA4QUFBRC8vLy8wLy8vLzlQLy8vL1E9PSJ9LHsiYyI6Ik0iLCJ3IjoyMSwiaCI6MTksInRvcCI6LTE5LCJhZHYiOjIzLCJweCI6IlAvZ0FBLytQL3dBQi8rUC93QUMvK1AvMEFELytQNzRBSDcrUDc4QUw3K1A3OUFQMytQNitBZnorUDUvQXZqK1A0L1EvVCtQNHZoL0QrUDRmeStEK1A0UDM5RCtQNEw3OEQrUDRILzREK1A0RC8wRCtQNEMvd0QrUDRCL2dEK1A0QS9RRCtBPT0ifSx7ImMiOiJOIiwidyI6MTgsImgiOjE5LCJ0b3AiOi0xOSwiYWR2IjoyMCwicHgiOiJQL0FBSDlQL1FBSDlQL3dBSDlQLzRBSDlQLzhBSDlQNytBSDlQMi9RSDlQNC93SDlQNGYwSDlQNFA4SDlQNEgrSDlQNEMvSDlQNEEvbjlQNEF2MzlQNEFQLzlQNEFILzlQNEFELzlQNEFCLzlQNEFBdjlBPSJ9LHsiYyI6Ik8iLCJ3IjoyMCwiaCI6MTksInRvcCI6LTE5LCJhZHYiOjIyLCJweCI6IkFCdi9vQUFBLy8vK0FBZi8vLy9BRC81Vi8vQXY5QUFmK0gvUUFBdjh2NEFBQS8yL1FBQUMvdjlBQUFMKy8wQUFBdjcvUUFBQy9yK0FBQVA5djhBQUEvMC8wQUFML0MvMEFCLzBELzVWdi9BSC8vLy93QUMvLy80QUFCdi9vQUE9In0seyJjIjoiUCIsInciOjE3LCJoIjoxOSwidG9wIjotMTksImFkdiI6MTksInB4IjoiUC8vL2tBLy8vLzRELy8vLzRQOEFXLzAvd0FDL2ovQUFIK1A4QUF2NC93QUQvai9BQi84UC8vLy9nLy8vLzRELy8vNUFQOEFBQUEvd0FBQUQvQUFBQVA4QUFBQS93QUFBRC9BQUFBUDhBQUFBIn0seyJjIjoiUSIsInciOjIwLCJoIjoyNCwidG9wIjotMTksImFkdiI6MjIsInB4IjoiQUJ2L29BQUEvLy8rQUFmLy8vL0FELzVWLy9BdjlBQWY5SC9RQUF2OHY0QUFBLzIvUUFBRC9mOUFBQUwrLzBBQUF2Ny9RQUFDL3I5QUFBTCt2NEFBQS8xLzBBQUwvQy93QUIvNEgvNUJ2L0FILy8vLzBBSC8vLzhBQUJ2LzVBQUFBTC9BQUFBQVArUUFBQUF2LytBQUFBdi80QUFBQWIvZyJ9LHsiYyI6IlIiLCJ3IjoxOSwiaCI6MTksInRvcCI6LTE5LCJhZHYiOjIwLCJweCI6IlAvLy81QUQvLy8vNEEvLy8vL2dQOEFGdjlEL0FBRC9nL3dBQXY0UDhBQUwrRC9BQUQvUS93QVgvd1AvLy8vMEQvLy8vMEEvLy8vZ0FQOEFQOUFEL0FCL3dBL3dBUCtBUDhBQS8wRC9BQUwvQS93QUEvNFA4QUFIL1FBPT0ifSx7ImMiOiJTIiwidyI6MTgsImgiOjE5LCJ0b3AiOi0xOSwiYWR2IjoxOSwicHgiOiJBQ3Yvb0FBdi8vL1FDLy8vLzBEL2dCLzhIL0FBUG9IL0FBQUFEL2dBQUFDLytrQUFBLy8vNEFBTC8vL2dBQWEvLzRBQUFCLzlBQUFBUCtBQUFBSCtLOEFBTCtQL1VCdjlILy8vLzRCLy8vL2dBRy8vb0FBPSJ9LHsiYyI6IlQiLCJ3IjoxNywiaCI6MTksInRvcCI6LTE5LCJhZHYiOjE3LCJweCI6InYvLy8vKy8vLy8vNy8vLy8vQUF2NEFBQUMvZ0FBQUwrQUFBQXY0QUFBQy9nQUFBTCtBQUFBdjRBQUFDL2dBQUFMK0FBQUF2NEFBQUMvZ0FBQUwrQUFBQXY0QUFBQy9nQUFBTCtBQUFBdjRBQSJ9LHsiYyI6IlUiLCJ3IjoxOCwiaCI6MTksInRvcCI6LTE5LCJhZHYiOjIwLCJweCI6ImY0QUFMK2Y0QUFMK2Y0QUFMK2Y0QUFMK2Y0QUFMK2Y0QUFMK2Y0QUFMK2Y0QUFMK2Y0QUFMK2Y0QUFMK2Y0QUFMK2Y0QUFMK2Y4QUFMK1A4QUFQOVArQUF2OEgvMVgvNEMvLy8vZ0F2Ly8rQUFHLytnQUE9In0seyJjIjoiViIsInciOjE5LCJoIjoxOSwidG9wIjotMTksImFkdiI6MTksInB4IjoidjRBQUQvWC9BQUIvdy8wQUF2NEwrQUFQOUEvd0FEL0FQOUFDL2dCL2dBL3dBUDhBUDRBQy9RTDlBQWY0RC9BQUQvQS9nQUF2d2YwQUFEK0w4QUFBL3orQUFBSDkvQUFBQS8vZ0FBQUwvMEFBQUIvOEFBQUFQK0FBQUE9PSJ9LHsiYyI6IlciLCJ3IjoyNywiaCI6MTksInRvcCI6LTE5LCJhZHYiOjI2LCJweCI6Ii8wQUQvZ0FQOXY0QUgvd0FQOGY0QUwvd0FmOFA4QVAvMEF2NFA4QVAvNEF2MEw5QWY3OEEvd0grQXZuOEEvZ0QvQS9qOUIvZ0QvQS9UK0MvUUMvUi9DL0QvQUIvaS9CL0QrQUEvaStBL1g5QUF2ejlBL3I4QUF2MzhBdnI4QUFmNzhBdi80QUFQLzRBZi8wQUFMLzBBUC93QUFIL3dBTC93QUFEL3dBTC9nQUEifSx7ImMiOiJYIiwidyI6MTksImgiOjE5LCJ0b3AiOi0xOSwiYWR2IjoxOSwicHgiOiJQOUFBTCtCL3dBSC9BTCtBRC9RQS8wQy9nQUgvQi93QUF2NC8wQUFEL3Y0QUFBUC84QUFBQy85QUFBQWYvUUFBQVAvOEFBQUwvL2dBQUgrUDlBQUQvQi93QUMvUUwrQUIvd0EvMEEvd0FIL0EvNEFBLzRmOEFBSC9BQT09In0seyJjIjoiWSIsInciOjE5LCJoIjoxOSwidG9wIjotMTksImFkdiI6MTksInB4IjoiZjhBQUgvQy9nQUQvUVA5QUMvZ0IvZ0Evd0FMOUF2MEFBL3dmOEFBTCtQOUFBQS83K0FBQUgvL0FBQUF2L1FBQUFEL2dBQUFBdjBBQUFBTDlBQUFBQy9RQUFBQXYwQUFBQUw5QUFBQUMvUUFBQUF2MEFBQUFMOUFBQUE9PSJ9LHsiYyI6IloiLCJ3IjoxNywiaCI6MTksInRvcCI6LTE5LCJhZHYiOjE3LCJweCI6IkQvLy8vZ1AvLy8rQS8vLy80QlZWWC9RQUFBLzBBQUFMK0FBQUMvd0FBQWY4QUFBRC9RQUFBLzBBQUFMK0FBQUMvd0FBQWY4QUFBRC9RQUFBLzBBQUFMK1ZWVlIvLy8vL1gvLy8vOWYvLy8vMCJ9LHsiYyI6IlsiLCJ3Ijo4LCJoIjoyNiwidG9wIjotMjAsImFkdiI6OSwicHgiOiJmLzkvLzMrcWYwQi9RSDlBZjBCL1FIOUFmMEIvUUg5QWYwQi9RSDlBZjBCL1FIOUFmMEIvUUg5QWYwQi9RSCtxZi85Ly93PT0ifSx7ImMiOiJcXCIsInciOjgsImgiOjIxLCJ0b3AiOi0yMCwiYWR2Ijo4LCJweCI6InZnQy9BSDhBUDBBL1FDK0FMOEFmd0EvQUQ5QVA0QXZnQi9BSDhBUDBBL2dDK0FMOEFmd0EvUUQ5In0seyJjIjoiXSIsInciOjgsImgiOjI2LCJ0b3AiOi0yMCwiYWR2Ijo5LCJweCI6InYvKy8vMnIvQVA4QS93RC9BUDhBL3dEL0FQOEEvd0QvQVA4QS93RC9BUDhBL3dEL0FQOEEvd0QvQVA4QS8yci92LysvL3c9PSJ9LHsiYyI6Il4iLCJ3IjoxNiwiaCI6MTIsInRvcCI6LTE5LCJhZHYiOjE2LCJweCI6IkFCLzRBQUF2L0FBQVA3NEFBTDUvQUFEOEwwQUMrQi9BQS9BUDBBZmdCK0FQMEFQMEg4QUMrQzlBQVB4L0FBQysifSx7ImMiOiJfIiwidyI6MTcsImgiOjIsInRvcCI6MiwiYWR2IjoxNiwicHgiOiJmLy8vLzhBQUFBQUEifSx7ImMiOiJgIiwidyI6OCwiaCI6NCwidG9wIjotMjAsImFkdiI6OSwicHgiOiJQOEFMOEFMOEFIND0ifSx7ImMiOiJhIiwidyI6MTYsImgiOjE1LCJ0b3AiOi0xNSwiYWR2IjoxNiwicHgiOiJBRy80QUFQLy8wQVAvci9BSC9BdjRCcVFIK0FBQUIvZ0F2Ly80QS8vLytBdjlCL2dQOEFmNEQvQUwrQS8wSC93UC92NytSLy8xLzhHL2dIKyJ9LHsiYyI6ImIiLCJ3IjoxNSwiaCI6MjAsInRvcCI6LTIwLCJhZHYiOjE3LCJweCI6IlA4QUFBUDhBQUFQOEFBQVA4QUFBUDhBQUFQOGIrQVA5Ly8wUC83LzhQL0FmOVA5QUwrUDhBSC9QOEFEL1A4QUQvUDhBRC9QOEFIL1A5QUwrUC9BZjlQLzYvOFA1Ly93UDRiK0EifSx7ImMiOiJjIiwidyI6MTQsImgiOjE1LCJ0b3AiOi0xNSwiYWR2IjoxNiwicHgiOiJBYi9rQUwvLzRDLzYvNFA5QS8yL2dCL3I5QUFBLzBBQUQvQUFBUDlBQUF2MEFBQy9nQi9qL1FQOUwvci93TC8vNEFHLzVBQT0ifSx7ImMiOiJkIiwidyI6MTUsImgiOjIwLCJ0b3AiOi0yMCwiYWR2IjoxNywicHgiOiJBQUFMOUFBQUw5QUFBTDlBQUFMOUFBQUw5QXY5TDlELy9yOUwvci85ZjlBdjl2NEFQOXYwQVA5LzBBTDkvMEFMOS8wQUw5djBBUDl2NEFmOWY5QS85TC9yLzlELy9yOUF2NUw5In0seyJjIjoiZSIsInciOjE0LCJoIjoxNSwidG9wIjotMTUsImFkdiI6MTYsInB4IjoiQWIvZ0FMLy8wQy82LzBQOEEvaS9RQi9MOUFIOS8vLy83Ly8vL3YrVlZWdjBBQUMvZ0FBRC9BTDhML3IvZ0wvLzRBRy81QUE9In0seyJjIjoiZiIsInciOjEwLCJoIjoyMCwidG9wIjotMjAsImFkdiI6OSwicHgiOiJBTC9RUC8wSC9wQi9nQWY0Qy8vOXYvL1d2K2tIK0FCL2dBZjRBSCtBQi9nQWY0QUgrQUIvZ0FmNEFIK0FCL2dBZjRBPSJ9LHsiYyI6ImciLCJ3IjoxNSwiaCI6MjEsInRvcCI6LTE1LCJhZHYiOjE3LCJweCI6IkF2OUw5RC8vcjlMLzcvOWY5QS85djRBZjl2MEFQOS8wQUw5LzBBTDkvMEFMOXYwQVA5djRBZjlmOUEvOVAvNy85RC8vcjlBdjVMOEFBQVA4QlVBUDhQOEF2NEwvci93Qy8vL1FBYi9vQUE9PSJ9LHsiYyI6ImgiLCJ3IjoxNSwiaCI6MjAsInRvcCI6LTIwLCJhZHYiOjE3LCJweCI6IlA4QUFBUDhBQUFQOEFBQVA4QUFBUDhBQUFQOEwrQVA5Ly8wUDcvLzhQL1F2OFArQVA5UDhBTDlQOEFMOVA4QUw5UDhBTDlQOEFMOVA4QUw5UDhBTDlQOEFMOVA4QUw5UDhBTDkifSx7ImMiOiJpIiwidyI6NSwiaCI6MjAsInRvcCI6LTIwLCJhZHYiOjgsInB4IjoiUDgveitBQUFEL1A4L3ovUDgvei9QOC96L1A4L3ovUDgvdz09In0seyJjIjoiaiIsInciOjcsImgiOjI2LCJ0b3AiOi0yMCwiYWR2Ijo4LCJweCI6IkEvd1A4RCtBQUFBQUQvQS93UDhEL0Evd1A4RC9BL3dQOEQvQS93UDhEL0Evd1A4RC9BL3dmNS8rdi9IK1FBPT0ifSx7ImMiOiJrIiwidyI6MTUsImgiOjIwLCJ0b3AiOi0yMCwiYWR2IjoxNiwicHgiOiJQOEFBQVA4QUFBUDhBQUFQOEFBQVA4QUFBUDhBZjRQOEIvd1A4RC9BUDhQOUFQOHYwQVArL1FBUC8vUUFQLy93QVAvdjRBUDhQOUFQOEgvQVA4Qy9nUDhBL3dQOEF2NFA4QVA5In0seyJjIjoibCIsInciOjUsImgiOjIwLCJ0b3AiOi0yMCwiYWR2Ijo4LCJweCI6IlA4L3ovUDgvei9QOC96L1A4L3ovUDgvei9QOC96L1A4L3c9PSJ9LHsiYyI6Im0iLCJ3IjoyMywiaCI6MTUsInRvcCI6LTE1LCJhZHYiOjI1LCJweCI6IlA0YjlBdjRBL24vOUwvOEQrLy85Ly80UC9SLytDL3cvMEMvd0QvRC9BTCtBUDhQOEFmNEF2MC93Qi9nQy9UL0FIK0FMOVA4QWY0QXYwL3dCL2dDL1QvQUgrQUw5UDhBZjRBdjAvd0IvZ0MvVC9BSCtBTDlBIn0seyJjIjoibiIsInciOjE1LCJoIjoxNSwidG9wIjotMTUsImFkdiI6MTcsInB4IjoiUDRMK0FQNS8vMFA3Ly84UC9RdjhQK0FQOVA4QUw5UDhBTDlQOEFMOVA4QUw5UDhBTDlQOEFMOVA4QUw5UDhBTDlQOEFMOVA4QUw5QSJ9LHsiYyI6Im8iLCJ3IjoxNSwiaCI6MTUsInRvcCI6LTE1LCJhZHYiOjE3LCJweCI6IkFMLzVBQi8vL2dILzcvNFA5QWY5djRBTCt2MEFILy8wQUQvL3dBRC8vMEFEL3YwQUgvZjRBTCtQOUFmOEgvNy8wQi8vL1FBTC80QUEifSx7ImMiOiJwIiwidyI6MTUsImgiOjIxLCJ0b3AiOi0xNSwiYWR2IjoxNywicHgiOiJQNGIrQVA1Ly8wUC83LzhQL0FmOVA5QUwrUDhBSC9QOEFEL1A4QUQvUDhBRC9QOEFIL1A5QUwrUC9BZjlQLzYvOFA5Ly93UDhiK0FQOEFBQVA4QUFBUDhBQUFQOEFBQVA4QUFBUDhBQUFBPT0ifSx7ImMiOiJxIiwidyI6MTUsImgiOjIxLCJ0b3AiOi0xNSwiYWR2IjoxNywicHgiOiJBdjlMOUQvL3I5TC83LzlmOUEvOXY0QWY5djBBUDkvMEFMOS8wQUw5LzBBTDl2MEFQOXY0QWY5ZjlBLzlML3IvOUQvL3I5QXY1TDlBQUFMOUFBQUw5QUFBTDlBQUFMOUFBQUw5QUFBTDlBPT0ifSx7ImMiOiJyIiwidyI6MTAsImgiOjE1LCJ0b3AiOi0xNSwiYWR2IjoxMSwicHgiOiJQNHZUK2Y0L3YrUC9sVC9nQS93QVA4QUQvQUEvd0FQOEFEL0FBL3dBUDhBRC9BQS93QUE9In0seyJjIjoicyIsInciOjE0LCJoIjoxNSwidG9wIjotMTUsImFkdiI6MTYsInB4IjoiQXYva0FmLy80RC9xLzRmMEF2aC9RQUFIL2xBQVAvL2tBTC8vOUFDdi84QUFCLzBBQUIvYjRBSDl2K3Evd3YvLzhBYi81QUE9In0seyJjIjoidCIsInciOjksImgiOjE4LCJ0b3AiOi0xOCwiYWR2Ijo5LCJweCI6IkF2QUEvQUIvQXYvL3YvL2IvcUQvQUQvQUQvQUQvQUQvQUQvQUQvQUQvQUQvUUMvNkIvL0FmK0E9In0seyJjIjoidSIsInciOjE1LCJoIjoxNSwidG9wIjotMTUsImFkdiI6MTcsInB4IjoiZjRBTDlmNEFMOWY0QUw5ZjRBTDlmNEFMOWY0QUw5ZjRBTDlmNEFMOWY0QVA5ZjRBUDlmOEFmOVArQi85TC8vNzlELy9iOUF2NUw5QSJ9LHsiYyI6InYiLCJ3IjoxNiwiaCI6MTUsInRvcCI6LTE1LCJhZHYiOjE2LCJweCI6InYwQUMvWCtBQS93L3dBZjRMOUFMOUIvZ0QvQVA4Qi9nQy9RdndBZjRQNEFEL0g5QUF2eS9BQUg5L2dBQS8vMEFBTC84QUFBLytBQUFQL1FBIn0seyJjIjoidyIsInciOjIzLCJoIjoxNSwidG9wIjotMTUsImFkdiI6MjIsInB4IjoiUDRBZjhBUDR2d0MvMEEvaS9BUC9nSDlIOUErL0F2d1A0SDc4QytBdmd2YjBQMEIvRDhmZy9BSDhQdy9IOEFQMStEOHZnQXZyMEwzOUFCLy9BZnZ3QUQvNEEvL0FBUC9nRC80QUF2OUFML1FBQi93QWY4QUEifSx7ImMiOiJ4IiwidyI6MTYsImgiOjE1LCJ0b3AiOi0xNSwiYWR2IjoxNiwicHgiOiJmOEFMK0MvZ0QvQVA5Qy9RQS94L2dBSCsvd0FBdi8wQUFELzBBQUF2OEFBQWYvd0FBUC8rQUFMOXYwQUgrRC9BRC9BZjREL1FEL1MvZ0FQOCJ9LHsiYyI6InkiLCJ3IjoxNiwiaCI6MjEsInRvcCI6LTE1LCJhZHYiOjE2LCJweCI6InY0QUQvWC9BQS93L3dBZjRIOUFMOEEvd0QvQUw4Qi9RQi9RdndBUDRQNEFDL0Q5QUFQMS9BQUMrdmdBQWYvMEFBRC84QUFBditBQUFEL0FBQUEvZ0FBQXYwQUFBZjhBQUwvOUFBQy8rQUFBdjlBQUEifSx7ImMiOiJ6IiwidyI6MTIsImgiOjE1LCJ0b3AiOi0xNSwiYWR2IjoxNCwicHgiOiJmLy85Zi8vOWYvLzlBQXY4QUIvd0FEL1FBTCtBQWY4QUEvMEFEL1FBTCtBQWY4QUEvLy8vLy8vLy8vLy8ifSx7ImMiOiJ7IiwidyI6MTEsImgiOjI2LCJ0b3AiOi0yMCwiYWR2IjoxMSwicHgiOiJBQy8wQXYvUUgvNUFmNEFCL1FBSDlBQWYwQUIvUUFIOUFBdjBBRC9BQnY0QXYvQUMvMEFILzBBQi93QUMvQUFMOUFBZjBBQi9RQUg5QUFmMEFCL2dBSC81QUwvMEFML1EifSx7ImMiOiJ8IiwidyI6NCwiaCI6MjYsInRvcCI6LTIwLCJhZHYiOjgsInB4IjoiL3Y3Ky92NysvdjcrL3Y3Ky92NysvdjcrL3Y3Ky92NysvdjQ9In0seyJjIjoifSIsInciOjExLCJoIjoyNiwidG9wIjotMjAsImFkdiI6MTEsInB4IjoiZitBQi8rQUcvOEFBLzBBQi9RQUg5QUFmMEFCL1FBSDlBQWYwQUIvZ0FEL2tBRC80QUgvZ0IvOUFQOUFCL2dBSDlBQWYwQUIvUUFIOUFBZjBBRC9RRy84QWYvZ0IvNEFBIn0seyJjIjoifiIsInciOjE1LCJoIjo1LCJ0b3AiOi0xMiwiYWR2IjoxNiwicHgiOiJMK1FBQS8vK0FkLy8vLzk0QnYvOVFBQy9rQT09In0seyJjIjoiXHUwMGUxIiwidyI6MTYsImgiOjIxLCJ0b3AiOi0yMSwiYWR2IjoxNiwicHgiOiJBQUQvQUFBRCtBQUFEK0FBQUM5QUFBQUFBQUFBQUFBQUFMLzRBQWYvLzBBUCtyL0FIK0F2MEJxUUgrQUFBQi9nQXYvLzRCLy8vK0EvNUIvZ1A4QWY0SC9BTCtCL3dML2dQL3Y3K1IvL3gvNEcvZ0w5In0seyJjIjoiXHUwMGU5IiwidyI6MTQsImgiOjIxLCJ0b3AiOi0yMSwiYWR2IjoxNiwicHgiOiJBQUgrQUFCL2dBQWYwQUFENEFBQUFBQUFBQUFBQWIvZ0FMLy8wQy82LzBQOEEvaS9RQi9MOUFIOS8vLy83Ly8vL3YrVlZWdjBBQUMvZ0FBRC9BTDhML3IvZ0wvLzRBRy81QUE9In0seyJjIjoiXHUwMGVkIiwidyI6OCwiaCI6MjEsInRvcCI6LTIxLCJhZHYiOjgsInB4IjoiQXYwSDlCL0FmZ0FBQUFBQVA4QS93RC9BUDhBL3dEL0FQOEEvd0QvQVA4QS93RC9BUDhBL3dEL0EifSx7ImMiOiJcdTAwZjMiLCJ3IjoxNSwiaCI6MjEsInRvcCI6LTIxLCJhZHYiOjE3LCJweCI6IkFBQy9RQUFMOUFBQXZnQUFDOUFBQUFBQUFBQUFBQUFMLzVBQi8vL2dILzcvNFA5QWY5djRBTCt2MEFILy8wQUQvL3dBRC8vMEFEL3YwQUgvZjRBTCtQOUFmOEgvNy8wQi8vL1FBTC80QUE9PSJ9LHsiYyI6Ilx1MDBmYSIsInciOjE1LCJoIjoyMSwidG9wIjotMjEsImFkdiI6MTcsInB4IjoiQUFDL1FBQUw5QUFBdmdBQUM5QUFBQUFBQUFBQUFBZjRBTDlmNEFMOWY0QUw5ZjRBTDlmNEFMOWY0QUw5ZjRBTDlmNEFMOWY0QVA5ZjRBUDlmOEFmOVArQi85TC8vNzlELy9iOUF2NUw5QT09In0seyJjIjoiXHUwMGYxIiwidyI6MTUsImgiOjIxLCJ0b3AiOi0yMSwiYWR2IjoxNywicHgiOiJBZjBEd0EvL3J3Qjl2L2dDNEMrQUFBQUFBQUFBQUFQNEwrQVA1Ly8wUDcvLzhQL1F2OFArQVA5UDhBTDlQOEFMOVA4QUw5UDhBTDlQOEFMOVA4QUw5UDhBTDlQOEFMOVA4QUw5UDhBTDlBPT0ifSx7ImMiOiJcdTAwYzEiLCJ3IjoyMCwiaCI6MjUsInRvcCI6LTI1LCJhZHYiOjIwLCJweCI6IkFBQUgrQUFBQUIvZ0FBQUFmMEFBQUFENEFBQUFBQUFBQUFBQUFBQUFBQUwvZ0FBQUEvL0FBQUFILzlBQUFBdjc4QUFBRCtmd0FBQWYwL2dBQUMvQy9BQUFQNEg5QUFCL1FQNEFBUDhBdndBQi9nQi9RQUwvLy8rQUEvLy8vOEFILy8vLzRBdjBBQS93RC9BQUMvUWY0QUFIK0QvUUFBUDhQOEFBQXYwPSJ9LHsiYyI6Ilx1MjBhYyIsInciOjE2LCJoIjoxOSwidG9wIjotMTksImFkdiI6MTYsInB4IjoiQUJ2K0FBQy8vOUFDLy8vd0EvMEwrQXY0QS9nUDhBQUFEL0FBQUwvLzlBQy8vL0FBSC9BQUFMLy85QUMvLy9BQUQvQUFBQS93QUFBTCtBUDhBLzRMK0FMLy8vUUF2Ly9RQUJ2K1FBPT0ifSx7ImMiOiJcdTIwMTMiLCJ3IjoxNSwiaCI6MywidG9wIjotOSwiYWR2IjoxNiwicHgiOiJmLy8vK2YvLy8rUC8vLytBIn0seyJjIjoiXHUyMDE0IiwidyI6MjgsImgiOjMsInRvcCI6LTksImFkdiI6MjgsInB4IjoiLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLyJ9LHsiYyI6Ilx1MjAxOCIsInciOjUsImgiOjgsInRvcCI6LTE5LCJhZHYiOjgsInB4IjoiRDR2RDBQUS96L1A4L3c9PSJ9LHsiYyI6Ilx1MjAxOSIsInciOjUsImgiOjgsInRvcCI6LTE5LCJhZHYiOjgsInB4IjoiUDgvei9QOEhndUQwdUE9PSJ9LHsiYyI6Ilx1MjAxYyIsInciOjEwLCJoIjo4LCJ0b3AiOi0xOSwiYWR2IjoxNCwicHgiOiJQZ1Bud0h5NEQ0OUE5UDhQLy9ELy93Ly84UDg9In0seyJjIjoiXHUyMDFkIiwidyI6MTAsImgiOjgsInRvcCI6LTE5LCJhZHYiOjE0LCJweCI6Ii93Ly84UC8vRC8vdy94OEI4dUF1UFFQYndMZz0ifSx7ImMiOiJcdTIwMjIiLCJ3Ijo5LCJoIjo4LCJ0b3AiOi0xMywiYWR2IjoxMCwicHgiOiJCdmdILzhQLytQLy9QLy9QLytILzhCdmcifSx7ImMiOiJcdTAwYjciLCJ3Ijo1LCJoIjo1LCJ0b3AiOi0xMiwiYWR2Ijo5LCJweCI6IkZRL3ovUDgvd0E9PSJ9XX0="


def _load_font():
    raw = json.loads(base64.b64decode(FONT_B64))
    glyphs = {}
    for g in raw["glyphs"]:
        data = base64.b64decode(g["px"]) if g["px"] else b""
        pixels = []
        for byte in data:
            for shift in (6, 4, 2, 0):
                pixels.append((byte >> shift) & 3)
        glyphs[g["c"]] = (g["w"], g["h"], g["top"], g["adv"], pixels)
    return raw["size"], glyphs


FONT_SIZE, GLYPHS = _load_font()
_MISSING = GLYPHS.get("?", (10, 10, -10, 10, [0] * 100))


def text_width(text, scale):
    """Width in pixels of text drawn at the given scale."""
    total = 0
    for ch in text:
        g = GLYPHS.get(ch, _MISSING)
        total += g[3]
    return int(total * scale)


def wrap_text(text, scale, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(bg * (w * h))

    def _idx(self, x, y):
        return (y * self.w + x) * 3

    def px(self, x, y, color, alpha=1.0):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self._idx(x, y)
            if alpha >= 1.0:
                self.buf[i : i + 3] = bytes(color)
            else:
                for k in range(3):
                    self.buf[i + k] = int(
                        self.buf[i + k] * (1.0 - alpha) + color[k] * alpha
                    )

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = self._idx(x0, yy)
            self.buf[i : i + (x1 - x0) * 3] = bytes(color) * (x1 - x0)

    def frame(self, x, y, w, h, color, t=2):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def hline(self, x, y, w, color, t=1):
        self.rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.rect(x, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        r = t // 2
        while True:
            self.rect(x - r, y - r, t, t, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            dx = int((r * r - dy * dy) ** 0.5) if r * r - dy * dy >= 0 else 0
            self.rect(cx - dx, yy, 2 * dx + 1, 1, color)

    def ellipse(self, cx, cy, rx, ry, color):
        for yy in range(cy - ry, cy + ry + 1):
            dy = (yy - cy) / ry if ry else 0
            dx = int(rx * (max(0.0, 1.0 - dy * dy)) ** 0.5)
            self.rect(cx - dx, yy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, t=3):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            outer = (r * r - dy * dy) ** 0.5 if r * r - dy * dy >= 0 else 0
            inner = ((r - t) * (r - t) - dy * dy) ** 0.5 if (r - t) ** 2 - dy * dy >= 0 else 0
            for xx in range(cx - int(outer), cx + int(outer) + 1):
                if abs(xx - cx) >= inner:
                    self.px(xx, yy, color)

    def poly(self, pts, color):
        # Scanline fill of a simple polygon.
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h - 1, max(ys)) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), y, int(xs[i + 1]) - int(xs[i]) + 1, 1, color)

    def text(self, x, y_baseline, s, scale, color):
        """Draw text with its baseline at y_baseline (font units scaled)."""
        cx = x
        for ch in s:
            g = GLYPHS.get(ch, _MISSING)
            w, h, top, adv, pixels = g
            if w and h:
                for row in range(h):
                    for col in range(w):
                        lvl = pixels[row * w + col]
                        if lvl:
                            a = lvl / 3.0
                            # Tile the source pixel over its scaled rect so
                            # neighbouring pixels meet with no gaps.
                            gx0 = int(cx + col * scale)
                            gx1 = int(cx + (col + 1) * scale)
                            gy0 = int(y_baseline + (top + row) * scale)
                            gy1 = int(y_baseline + (top + row + 1) * scale)
                            if gx1 <= gx0:
                                gx1 = gx0 + 1
                            if gy1 <= gy0:
                                gy1 = gy0 + 1
                            for by in range(gy0, gy1):
                                for bx in range(gx0, gx1):
                                    self.px(bx, by, color, a)
            cx += int(adv * scale)
        return cx

    def text_centred(self, cx, y_baseline, s, scale, color):
        self.text(cx - text_width(s, scale) // 2, y_baseline, s, scale, color)

    # ------------------------------------------------------------- PNG out
    def write_png(self, path):
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)  # filter: None
            raw += self.buf[y * stride : (y + 1) * stride]
        comp = zlib.compress(bytes(raw), 9)

        def chunk(tag, data):
            out = struct.pack(">I", len(data)) + tag + data
            out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
            return out

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        png = (
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp)
            + chunk(b"IEND", b"")
        )
        Path(path).write_bytes(png)
        return len(png)

# ------------------------------------------------------------------ colours
PAPER = (251, 247, 238)
INK = (20, 20, 20)
GREY = (96, 92, 82)
RED = (180, 35, 24)
NAVY = (27, 58, 92)
TEAL = (15, 118, 110)
GOLD = (180, 83, 9)
BLUE = (29, 78, 216)
WHITE = (255, 255, 255)
SKY = (214, 232, 244)
SAND = (243, 230, 205)
ORANGE = (234, 88, 12)
GREEN = (21, 128, 61)


def _tint(c, f=0.88):
    return tuple(int(255 * f + v * (1 - f)) for v in c)


# -------------------------------------------------------------------- icons
# Each icon draws a small flat scene inside the box (bx, by, bw, bh).
def icon_tanker(c, bx, by, bw, bh):
    c.rect(bx, by, bw, bh, SKY)
    c.rect(bx, by + int(bh * 0.62), bw, bh - int(bh * 0.62), (46, 110, 180))
    # mines in the water
    for mx, my in ((0.16, 0.78), (0.82, 0.84)):
        x, y = bx + int(bw * mx), by + int(bh * my)
        c.disc(x, y, 7, INK)
        for dx, dy in ((-9, 0), (9, 0), (0, -9), (0, 9), (-6, -6), (6, -6)):
            c.line(x, y, x + dx, y + dy, INK, 2)
    # hull
    hx, hy, hw, hh = bx + int(bw * 0.14), by + int(bh * 0.42), int(bw * 0.72), int(bh * 0.20)
    c.poly([(hx, hy), (hx + hw, hy), (hx + hw - 14, hy + hh), (hx + 14, hy + hh)], (30, 41, 59))
    c.rect(hx + int(hw * 0.62), hy - int(bh * 0.16), int(hw * 0.22), int(bh * 0.16), WHITE)
    c.rect(hx + int(hw * 0.62), hy - int(bh * 0.24), 5, int(bh * 0.08), INK)
    # flames above the hull
    fx = hx + int(hw * 0.30)
    c.poly([(fx, hy - 6), (fx + 12, hy - 34), (fx + 20, hy - 10), (fx + 32, hy - 40),
            (fx + 42, hy - 6)], ORANGE)
    c.poly([(fx + 8, hy - 6), (fx + 18, hy - 26), (fx + 28, hy - 6)], (250, 204, 21))
    # waves
    for wy in (0.70, 0.88):
        y = by + int(bh * wy)
        for k in range(4):
            x = bx + 8 + k * int(bw * 0.24)
            c.line(x, y, x + 14, y - 5, WHITE, 2)
            c.line(x + 14, y - 5, x + 28, y, WHITE, 2)


def icon_balloon(c, bx, by, bw, bh):
    c.rect(bx, by, bw, bh, (226, 232, 240))
    # storm cloud
    for cx, cy, r in ((0.26, 0.22, 16), (0.38, 0.16, 20), (0.52, 0.22, 15)):
        c.disc(bx + int(bw * cx), by + int(bh * cy), r, (71, 85, 105))
    # lightning
    lx, ly = bx + int(bw * 0.34), by + int(bh * 0.30)
    c.poly([(lx, ly), (lx + 12, ly), (lx + 4, ly + 18), (lx + 14, ly + 18),
            (lx - 2, ly + 42), (lx + 2, ly + 20), (lx - 8, ly + 20)], (250, 204, 21))
    # parade balloon
    ex, ey = bx + int(bw * 0.70), by + int(bh * 0.40)
    c.ellipse(ex, ey, int(bw * 0.15), int(bh * 0.32), RED)
    c.ellipse(ex - 8, ey - 10, 9, 6, (220, 60, 50))
    c.line(ex - 10, ey + int(bh * 0.28), ex - 16, ey + int(bh * 0.40), INK, 2)
    c.line(ex + 10, ey + int(bh * 0.28), ex + 16, ey + int(bh * 0.40), INK, 2)
    c.rect(ex - 16, ey + int(bh * 0.40), 32, 12, (120, 53, 15))
    # rain
    for k in range(5):
        x = bx + 10 + k * 14
        c.line(x, by + int(bh * 0.62), x - 5, by + int(bh * 0.78), (59, 130, 246), 2)


def icon_ballot(c, bx, by, bw, bh):
    c.rect(bx, by, bw, bh, SAND)
    # ballot box
    x, y, w, h = bx + int(bw * 0.30), by + int(bh * 0.38), int(bw * 0.40), int(bh * 0.44)
    c.rect(x, y, w, h, NAVY)
    c.rect(x - 6, y - 10, w + 12, 12, (15, 35, 60))
    # paper slip going in
    c.poly([(x + 14, y - 34), (x + 44, y - 34), (x + 44, y - 8), (x + 14, y - 8)], WHITE)
    c.line(x + 20, y - 26, x + 38, y - 26, GREY, 2)
    c.line(x + 20, y - 18, x + 38, y - 18, GREY, 2)
    # big check
    c.line(bx + int(bw * 0.10), by + int(bh * 0.55), bx + int(bw * 0.20), by + int(bh * 0.68), GREEN, 6)
    c.line(bx + int(bw * 0.20), by + int(bh * 0.68), bx + int(bw * 0.30), by + int(bh * 0.42), GREEN, 6)
    # euro coin
    cx, cy = bx + int(bw * 0.80), by + int(bh * 0.26)
    c.disc(cx, cy, 18, GOLD)
    c.ring(cx, cy, 18, (146, 64, 14), 2)
    c.text(cx - 6, cy + 7, "E", 0.62, WHITE)


def icon_blast(c, bx, by, bw, bh):
    c.rect(bx, by, bw, bh, (254, 226, 226))
    # buildings
    for fx, fw, fh in ((0.08, 0.20, 0.55), (0.32, 0.24, 0.72), (0.60, 0.22, 0.48)):
        x = bx + int(bw * fx)
        c.rect(x, by + bh - int(bh * fh), int(bw * fw), int(bh * fh), (51, 65, 85))
        for wy in range(3):
            c.rect(x + 5, by + bh - int(bh * fh) + 8 + wy * 16, 6, 8, (250, 204, 21))
    # starburst
    cx, cy = bx + int(bw * 0.58), by + int(bh * 0.30)
    pts = []
    import math
    for i in range(16):
        ang = i * math.pi / 8
        r = 30 if i % 2 == 0 else 13
        pts.append((cx + int(r * math.cos(ang)), cy + int(r * math.sin(ang))))
    c.poly(pts, ORANGE)
    c.disc(cx, cy, 9, (250, 204, 21))


def icon_dove(c, bx, by, bw, bh):
    c.rect(bx, by, bw, bh, (204, 231, 225))
    # olive branch
    c.line(bx + int(bw * 0.10), by + int(bh * 0.82), bx + int(bw * 0.42), by + int(bh * 0.55), GREEN, 3)
    for lx, ly in ((0.16, 0.74), (0.24, 0.66), (0.32, 0.60)):
        c.ellipse(bx + int(bw * lx), by + int(bh * ly), 10, 5, GREEN)
    # dove
    cx, cy = bx + int(bw * 0.62), by + int(bh * 0.48)
    c.ellipse(cx, cy, 34, 18, WHITE)
    c.disc(cx + 32, cy - 12, 10, WHITE)
    c.poly([(cx + 40, cy - 14), (cx + 52, cy - 10), (cx + 40, cy - 8)], ORANGE)
    c.disc(cx + 35, cy - 15, 2, INK)
    c.poly([(cx - 20, cy - 6), (cx + 6, cy - 30), (cx + 14, cy - 4)], (226, 232, 240))
    c.line(cx - 26, cy + 14, cx - 34, cy + 26, INK, 2)
    c.line(cx - 18, cy + 16, cx - 22, cy + 28, INK, 2)


def icon_monitor(c, bx, by, bw, bh):
    c.rect(bx, by, bw, bh, (219, 234, 254))
    # screen
    x, y, w, h = bx + int(bw * 0.22), by + int(bh * 0.14), int(bw * 0.56), int(bh * 0.58)
    c.rect(x, y, w, h, NAVY)
    c.rect(x + 5, y + 5, w - 10, h - 10, (30, 64, 175))
    c.text(x + w // 2 - 8, y + h - 16, "!", 1.0, WHITE)
    c.rect(x + w // 2 - 3, by + int(bh * 0.72), 6, int(bh * 0.10), NAVY)
    c.rect(x - 14, by + int(bh * 0.82), w + 28, 6, NAVY)
    # warning triangle
    tx, ty = bx + int(bw * 0.82), by + int(bh * 0.24)
    c.poly([(tx, ty - 14), (tx + 16, ty + 12), (tx - 16, ty + 12)], (250, 204, 21))
    c.text(tx - 2, ty + 9, "!", 0.5, INK)


def icon_boat(c, bx, by, bw, bh):
    c.rect(bx, by, bw, bh, SKY)
    c.disc(bx + int(bw * 0.82), by + int(bh * 0.20), 14, (250, 204, 21))
    c.rect(bx, by + int(bh * 0.66), bw, bh - int(bh * 0.66), (46, 110, 180))
    # hull
    hx, hy = bx + int(bw * 0.18), by + int(bh * 0.52)
    c.poly([(hx, hy), (hx + int(bw * 0.56), hy), (hx + int(bw * 0.48), hy + 20),
            (hx + int(bw * 0.08), hy + 20)], (120, 53, 15))
    # sail
    c.poly([(hx + int(bw * 0.30), hy - 4), (hx + int(bw * 0.30), hy - 52),
            (hx + int(bw * 0.52), hy - 4)], WHITE)
    c.line(hx + int(bw * 0.30), hy - 52, hx + int(bw * 0.30), hy, INK, 2)
    # people dots on the boat
    for px in (0.30, 0.38, 0.46):
        c.disc(bx + int(bw * px), hy - 8, 4, INK)
    # waves
    for wy in (0.76, 0.90):
        y = by + int(bh * wy)
        for k in range(4):
            x = bx + 8 + k * int(bw * 0.24)
            c.line(x, y, x + 14, y - 5, WHITE, 2)
            c.line(x + 14, y - 5, x + 28, y, WHITE, 2)


def icon_candle(c, bx, by, bw, bh):
    c.rect(bx, by, bw, bh, (233, 213, 255))
    # glow
    c.disc(bx + bw // 2, by + int(bh * 0.30), 26, (254, 243, 199))
    # flame
    cx, cy = bx + bw // 2, by + int(bh * 0.30)
    c.poly([(cx, cy - 22), (cx + 11, cy + 2), (cx + 5, cy + 10), (cx - 5, cy + 10),
            (cx - 11, cy + 2)], ORANGE)
    c.ellipse(cx, cy + 4, 5, 7, (250, 204, 21))
    # candle + base
    c.rect(cx - 9, cy + 12, 18, int(bh * 0.42), WHITE)
    c.frame(cx - 9, cy + 12, 18, int(bh * 0.42), GREY, 1)
    c.rect(bx + int(bw * 0.22), by + int(bh * 0.86), int(bw * 0.56), 5, INK)


# ------------------------------------------------------------------- panels
def panel(c, x, y, w, h, accent, tag, headline, deck, icon, tint,
          head_scale=0.92, deck_scale=0.62, icon_h=84):
    c.rect(x, y, w, h, WHITE)
    c.frame(x, y, w, h, INK, 2)
    c.rect(x, y, w, 7, accent)
    c.text(x + 16, y + 34, tag, 0.58, accent)
    ix, iy = x + 16, y + 44
    iw, ih = w - 32, icon_h
    c.rect(ix, iy, iw, ih, tint)
    c.frame(ix, iy, iw, ih, (210, 205, 190), 1)
    icon(c, ix, iy, iw, ih)
    ty = iy + ih + 14
    for line in wrap_text(headline, head_scale, w - 32)[:3]:
        c.text(x + 16, ty + int(21 * head_scale), line, head_scale, INK)
        ty += int(34 * head_scale)
    ty += 2
    for line in wrap_text(deck, deck_scale, w - 32)[:3]:
        c.text(x + 16, ty + int(19 * deck_scale), line, deck_scale, GREY)
        ty += max(20, int(26 * deck_scale))

# -------------------------------------------------------------------- build
def build():
    c = Canvas(1024, 1024, PAPER)
    # Masthead
    c.text_centred(512, 44, "THE WORLD IN ONE IMAGE", 0.78, RED)
    c.text_centred(512, 100, "THURSDAY 26 NOVEMBER 2026", 1.85, INK)
    c.text_centred(
        512, 128,
        "The day's biggest stories — from New York to the Strait of Hormuz",
        0.60, GREY,
    )
    c.hline(28, 138, 968, INK, 3)
    c.hline(28, 144, 968, INK, 1)

    # Lead row (taller panels, bigger pictures)
    panel(c, 28, 152, 520, 296, RED, "MIDDLE EAST  •  STRAIT OF HORMUZ",
          "TANKERS ABLAZE AFTER SEA-MINE BLASTS",
          "Iran says two tankers hit mines off Oman's Khasab port and caught "
          "fire. One was a supertanker carrying over 2 million barrels of crude.",
          icon_tanker, _tint(RED), head_scale=1.05, deck_scale=0.64, icon_h=100)
    panel(c, 564, 152, 432, 296, BLUE, "UNITED STATES",
          "PARADE POSTPONED BY STORM",
          "Macy's 100th parade moves to Saturday. Storm cuts power to 900,000.",
          icon_balloon, _tint(BLUE), head_scale=1.05, deck_scale=0.64, icon_h=100)

    # Second row
    panel(c, 28, 464, 312, 246, GOLD, "EUROPE  •  SPAIN",
          "SPAIN VOTES SUNDAY",
          "Sánchez calls a snap vote; EU picks de Cos as next ECB chief.",
          icon_ballot, _tint(GOLD), deck_scale=0.60, icon_h=72)
    panel(c, 356, 464, 312, 246, RED, "UKRAINE WAR",
          "STRIKES KILL 3 IN KHARKIV",
          "Russia hits homes and a school; Kyiv warns of a new mass strike.",
          icon_blast, _tint(RED), deck_scale=0.60, icon_h=72)
    panel(c, 684, 464, 312, 246, TEAL, "DIPLOMACY  •  GAZA",
          "CAIRO TALKS ON GAZA TRUCE",
          "Qatar and Egypt meet in Cairo to push the Gaza truce forward.",
          icon_dove, _tint(TEAL), deck_scale=0.60, icon_h=72)

    # Third row
    panel(c, 28, 726, 312, 236, NAVY, "TECHNOLOGY",
          "OUTAGE HITS DAY TWO",
          "Outlook and Teams down in 70+ countries; hospitals, schools hit.",
          icon_monitor, _tint(NAVY), deck_scale=0.60, icon_h=64)
    panel(c, 356, 726, 312, 236, BLUE, "MIGRATION  •  SPAIN",
          "RECORD DAY AT SEA",
          "More than 2,100 migrants reach the Canary Islands in a day.",
          icon_boat, _tint(BLUE), deck_scale=0.60, icon_h=64)
    panel(c, 684, 726, 312, 236, (124, 58, 237), "ASIA  •  INDIA",
          "18 YEARS SINCE 26/11",
          "Mumbai marks 18 years since the 2008 attacks.",
          icon_candle, (233, 213, 255), deck_scale=0.60, icon_h=64)

    # Also-today strip (one line)
    c.rect(28, 974, 968, 30, WHITE)
    c.frame(28, 974, 968, 30, INK, 2)
    c.text(44, 996, "ALSO TODAY", 0.56, RED)
    c.text(178, 996, "Guinea-Bissau vote delayed to 2028  •  Jazan refinery hit, "
           "1 killed  •  NATO over Poland  •  Tidal drops AI tracks",
           0.56, INK)

    # Footer
    c.text_centred(
        512, 1019,
        "Sources: Reuters, CNN, The Wall Street Journal, Daily Summary of World — 26 November 2026",
        0.50, GREY,
    )
    return c


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    size = build().write_png(path)
    print(f"wrote {path} ({size} bytes, 1024x1024)")


if __name__ == "__main__":
    main()
