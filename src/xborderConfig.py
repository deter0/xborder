from enum import Enum

import argparse

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
  
  parser = None
  def __init__(self):
    self.parser = argparse.ArgumentParser()
  
  def PraseColor(self, color_string: str) -> int|Color:
    color_string_copy = color_string
    prased_color: Color = Color()

    if (color_string[0] == '#'):
      try:
        literal_value = int(color_string.replace('#', "0x"), 16)
        if (len(color_string) == 4):
          prased_color.r = literal_value >> (8 * 3) & 0xFF
          prased_color.g = literal_value >> (8 * 2) & 0xFF
          prased_color.b = literal_value >> (8 * 1) & 0xFF
          prased_color.a = literal_value >> (8 * 0) & 0xFF
        elif (len(color_string) == 3):
          prased_color.r = literal_value >> (8 * 2) & 0xFF
          prased_color.g = literal_value >> (8 * 1) & 0xFF
          prased_color.b = literal_value >> (8 * 0) & 0xFF
          return prased_color
        return 0
      except:
        return 0
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
      return 0
  
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
    self.borderColor = self.PraseColor(args.border_color)
    self.borderThickness = args.border_thickness or 2
    self.disableUpdatePrompt = args.disable_update_prompt
    self.smartHideBorder = args.smart_hide_border
    
    positive_offset = self.PraseOffset(args.positive_offset)
    negative_offset = self.PraseOffset(args.negative_offset)
    self.offsets = [positive_offset[0], positive_offset[1], negative_offset[0], negative_offset[1]]