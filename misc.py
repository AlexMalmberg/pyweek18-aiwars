

FLOP_PREFIX = [
  '', 'kilo', 'mega', 'giga', 'tera', 'peta', 'exa', 'zetta', 'yotta']
FLOP_PREFIX_SHORT = [
  '', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
# If we need more we'll just make some up.


def FormatFlops(flops):
  """Formats a flops scalar."""
  i = 0
  while flops > 1000 and i < len(FLOP_PREFIX) - 1:
    flops /= 1000.
    i += 1
  if flops > 100:
    return '%3.0f %sflops' % (flops, FLOP_PREFIX[i])
  elif flops > 10:
    return '%4.1f %sflops' % (flops, FLOP_PREFIX[i])
  else:
    return '%4.2f %sflops' % (flops, FLOP_PREFIX[i])


def FormatFlopsShort(flops):
  """Formats a flops scalar. Will always fit in 4 chars if <1e27-ish."""
  i = 0
  while flops > 1 and i < len(FLOP_PREFIX_SHORT) - 1:
    flops /= 1000.
    i += 1
  if flops > 100:
    return '%3.0f%s' % (flops, FLOP_PREFIX_SHORT[i])
  elif flops > 10:
    return '%4.1f%s' % (flops, FLOP_PREFIX_SHORT[i])
  else:
    return '%4.2f%s' % (flops, FLOP_PREFIX_SHORT[i])
