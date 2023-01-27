from enum import Enum

import argparse
import json

class BorderMode(Enum):
  INSIDE = 0
  CENTER = 1
  OUTSIDE = 2

class Color:
  r: float = 0
  g: float = 0
  b: float = 0
  a: float = 1.0

class xborderConfig:
  borderMode: BorderMode = BorderMode.CENTER
  borderRadius: float = 14.0
  borderColor: Color = Color()
  borderThickness: float = 2.0
  smartHideBorder: bool = False
  disableUpdatePrompt: bool = False
  offsets: tuple[float] = [0, 0, 0, 0]
  printVersion: bool = True
  windowBlacklist: list[str] = []
  
  parser = None
  def __init__(self):
    self.parser = argparse.ArgumentParser()
  
  def BorderModeStrToEnum(self, border_mode: str) -> BorderMode|None:
    if border_mode.lower() == "outside":
      return BorderMode.OUTSIDE
    elif border_mode.lower() == "inside":
      return BorderMode.INSIDE
    elif border_mode.lower() == "center":
      return BorderMode.CENTER
    else:
      return None
  
  def PraseColor(self, color_string: str) -> int|None:
    color_string_copy = color_string
    prased_color: Color = Color()

    if (color_string[0] == '#'):
      try:
        literal_value = int(color_string.replace('#', "0x"), 16)
        if (len(color_string) == 2*4+1):
          prased_color.r = (literal_value >> (8 * 3) & 0xFF) / 255.0
          prased_color.g = (literal_value >> (8 * 2) & 0xFF) / 255.0
          prased_color.b = (literal_value >> (8 * 1) & 0xFF) / 255.0
          prased_color.a = (literal_value >> (8 * 0) & 0xFF) / 255.0
          return prased_color
        elif (len(color_string) == 2*3+1):
          prased_color.r = (literal_value >> (8 * 2) & 0xFF) / 255.0
          prased_color.g = (literal_value >> (8 * 1) & 0xFF) / 255.0
          prased_color.b = (literal_value >> (8 * 0) & 0xFF) / 255.0
          return prased_color
        return None
      except:
        return None
    elif (color_string.startswith('rgba')):
      color_string = color_string.replace("rgba(", "").replace(")", "")
      values = color_string.split(",")
      for i in range(len(values)):
        values[i] = float(values[i].rstrip().lstrip())
        if (values[i] > 1.0):
          values[i] /= 255.0
      
      if (len(values) < 4):
        raise ValueError(f"Got RGBA value: '{color_string_copy}' with less than 3 components.")
      
      prased_color.r = values[0]
      prased_color.g = values[1]
      prased_color.b = values[2]
      prased_color.a = values[3]
      
      return prased_color
    elif (color_string.startswith('rgb')):
      color_string = color_string.replace("rgb(", "").replace(")", "")
      values = color_string.split(",")
      for i in range(len(values)):
        values[i] = float(values[i].rstrip().lstrip())
        if (values[i] > 255):
          values[i] /= 255.0
          
      if (len(values) < 3):
        raise ValueError(f"Got RGBA value: '{color_string_copy}' with less than 3 components.")

      prased_color.r = values[0]
      prased_color.g = values[1]
      prased_color.b = values[2]
      
      return prased_color
    else:
      return None
  
  def ParseConfigFile(self, configFilePath: str) -> None:
    configFile = open(configFilePath, "r")
    configFileContent = configFile.read()
    configFile.close()
    
    configFileDecoded = json.loads(configFileContent)
    
    if (configFileDecoded['border-mode'] != None):
      self.borderMode = self.BorderModeStrToEnum(configFileDecoded['border-mode']) or self.borderMode
    
    if (configFileDecoded['border-color'] != None):
      self.borderColor = self.PraseColor(configFileDecoded['border-color']) or self.borderColor
    
    if (configFileDecoded['border-thickness'] != None):
      self.borderThickness = float(configFileDecoded['border-thickness']) or self.borderThickness
    
    if (configFileDecoded['border-radius'] != None):
      self.borderRadius = float(configFileDecoded['border-radius']) or self.borderRadius
    
    if (configFileDecoded['disable-update-prompt'] != None):
      self.disableUpdatePrompt = bool(configFileDecoded['disable-update-prompt'])
    
    if (configFileDecoded['positive-offset'] != None):
      self.offsets[0] = configFileDecoded['positive-offset'][0]
      self.offsets[1] = configFileDecoded['positive-offset'][1]
    
    if (configFileDecoded['negative-offset'] != None):
      self.offsets[2] = configFileDecoded['negative-offset'][0]
      self.offsets[3] = configFileDecoded['negative-offset'][1]
      
    if (configFileDecoded['blacklist-windows'] != None):
      self.windowBlacklist = configFileDecoded['blacklist-windows']
  
  def PraseOffset(self, original_offset_string: str) -> tuple[float]:
    offset_string = original_offset_string.replace("[", "").replace("]", "")
    offsets = offset_string.split(',')
    for i in range(len(offsets)):
      offsets[i] = float(offsets[i].rstrip().lstrip())
    if len(offsets) < 2:
      raise RuntimeError(f"Invalid offset parameter: {original_offset_string}, using 0")
      return [0, 0]
    return [offsets[0], offsets[1]]
  
  def ParseCmlArgs(self):
    self.parser.add_argument(
      "--config", "-c",
      type=str,
      help="The path to the config file"
    )
    self.parser.add_argument(
      "--border-radius",
      type=int,
      default=14.0,
      help="The border radius, in pixels"
    )
    self.parser.add_argument(
      "--border-thickness",
      type=int,
      default=4,
      help="The border thickness in pixels"
    )
    self.parser.add_argument(
      "--border-color",
      default="rgba(123, 88, 220, 1.0)",
      type=str,
      help="The colour of the border, examples: '#FF0000FF', 'rgb(24, 24, 24)', 'rgba(0.4, 0.8, 0.2, 0.5)' NOTE: If any value is greater than 1.0 it will be divided by 255",
    )
    self.parser.add_argument(
      "--border-mode",
      type=str,
      default="outside",
      help="Whether to place the border on the outside, inside or in the center of windows. Values are `outside`, `inside`, `center`"
    )
    self.parser.add_argument(
      "--smart-hide-border",
      action='store_true',
      help="Don't display a border if the window is alone in the workspace."
    )
    self.parser.add_argument(
      "--disable-update-prompt",
      action='store_true',
      help="Send a notification if xborders is out of date."
    )
    self.parser.add_argument(
      "--positive-offset",
      default="[0, 0]",
      type=str,
      help="How much to increase the windows size to the right and down, example: '[12, 16]'."
    )
    self.parser.add_argument(
      "--negative-offset",
      default="[0, 0]",
      type=str,
      help="How much to increase the windows size to the left and up, example '[12, 24]."
    )
    self.parser.add_argument(
      "--version",
      action="store_true",
      help="Print the version of xborders and exit."
    )
    
    args = self.parser.parse_args()
    
    self.printVersion = args.version == True
    
    if args.border_mode.lower() == "outside":
      self.borderMode = BorderMode.OUTSIDE
    elif args.border_mode.lower() == "inside":
      self.borderMode = BorderMode.INSIDE
    elif args.border_mode.lower() == "center":
      self.borderMode = BorderMode.CENTER
    
    self.borderRadius = args.border_radius
    parsedColor = self.PraseColor(args.border_color)
    self.borderColor = parsedColor if (parsedColor != 0) else Color()

    self.borderThickness = args.border_thickness or 2
    self.disableUpdatePrompt = args.disable_update_prompt
    self.smartHideBorder = args.smart_hide_border
    
    positive_offset = self.PraseOffset(args.positive_offset)
    negative_offset = self.PraseOffset(args.negative_offset)
    self.offsets = [positive_offset[0], positive_offset[1], negative_offset[0], negative_offset[1]]
    
    if args.config:
      self.ParseConfigFile(args.config)