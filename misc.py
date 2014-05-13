import math


import game


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


def DayProbToHourProb(prob):
  """
  If an event has a given probability to happen in 1 day, what's the
  probability that it'll happen each hour, assuming independent chance
  of happening in each hour and overall probability in 1 day should
  match what's given.
  """
  if prob > 0.9999:
    # Should really only be ~0.31 here, but meh, nobody should
    # complain that a 99.99% event happens immediately.
    return 1
  return 1 - math.exp(math.log1p(-prob) / 24.)


def StealDiscoverProb(my_crypto, their_crypto, steal_fraction):
  """Returns probability of being discovered each day."""
  steal_difficulty = 1 / (1 - steal_fraction / 105.) - 1
  difficulty = their_crypto + steal_difficulty
  delta = difficulty - my_crypto
  prob = 0.01 * math.exp(delta)
  if prob > 1:
    return 1
  return prob
