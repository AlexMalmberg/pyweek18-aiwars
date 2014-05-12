import a_crack
import a_research
import game
import misc
import n_datacenter
import vec


def main():
  gs = game.GameState()

  n1 = n_datacenter.Datacenter(vec.Vec(5, 5), 2.4e6, 1)
  gs.AddNode(n1)

  n2 = n_datacenter.Datacenter(vec.Vec(6, 6), 1.5e6, 0)
  gs.AddNode(n2)
  n2.control = True
  n2.flops_steal_fraction = 20

  gs.StartTurn()
  gs.Print()

  #a = a_crack.Crack(gs, n2)
  #print misc.FormatFlops(a.Cost())

  a = a_crack.Crack(gs, n1)
  print misc.FormatFlops(a.Cost())

  a = a_research.Research(gs, game.Research.Cracking)
  print misc.FormatFlops(a.Cost())
  gs.ExecuteAction(a)
  gs.Print()

  a = a_research.Research(gs, game.Research.Cracking)
  print misc.FormatFlops(a.Cost())
  gs.ExecuteAction(a)
  gs.Print()

  a = a_research.Research(gs, game.Research.Cracking)
  print misc.FormatFlops(a.Cost())

  a = a_crack.Crack(gs, n1)
  print misc.FormatFlops(a.Cost())
  gs.ExecuteAction(a)
  gs.Print()

  gs.EndTurn()
  gs.StartTurn()
  gs.Print()


if __name__ == '__main__':
  main()
