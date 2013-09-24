style_normal = "\033[0m"
style_great_success = "\033[1;32m"
style_success = "\033[32m"
style_error = "\033[31m"
style_warning = "\033[33m"
style_info = "\033[0m"
style_stealthy = "\033[1;37m"

def __generic_style(c):
  def _x(s, rl=False):
    return c + s + style_normal
  return _x

success = __generic_style(style_success)
error = __generic_style(style_error)
warning = __generic_style(style_warning)
great_success = __generic_style(style_great_success)
stealthy = __generic_style(style_stealthy)
info = __generic_style(style_info)

def base32hex(s):
  ctable = '0123456789abcdefghijklmnopqrstuv'
  return "".join([ ctable.index(c) for c in s])

