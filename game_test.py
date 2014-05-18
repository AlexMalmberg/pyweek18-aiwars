import a_app
import a_botnet
import a_crack
import a_research
import game
import misc
import n_city
import n_datacenter
import n_factory
import n_mine
import vec


def main():
  gs = game.GameState()

  nc = n_city.City(vec.Vec(1, 1), 1e6)
  gs.AddNode(nc)

  n1 = n_datacenter.Datacenter(vec.Vec(5, 5), 1, 2.4e6)
  gs.AddNode(n1)

  n2 = n_datacenter.Datacenter(vec.Vec(6, 6), 0, 1.5e6)
  gs.AddNode(n2)
  n2.control = True

  n3 = n_mine.Mine(vec.Vec(7, 7), 0, 4)
  gs.AddNode(n3)

  n4 = n_factory.Factory(vec.Vec(8, 8), 0, 4)
  gs.AddNode(n4)

  gs.Print()

  a = a_crack.Crack(gs, n1)
  print misc.FormatFlops(a.Cost())

  a = a_research.Research(gs, game.Research.Cracking)
  print misc.FormatFlops(a.Cost())

  gs.SetCurrentAction(a)
  gs.Print()

  for _ in xrange(34):
    gs.AdvanceTurn()
    gs.Print()

  a = a_crack.Crack(gs, n1)
  print misc.FormatFlops(a.Cost())
  gs.SetCurrentAction(a)
  gs.Print()

  for _ in xrange(267):
    gs.AdvanceTurn()
    gs.Print()

  gs.Print()

  a = a_crack.Crack(gs, n3)
  gs.SetCurrentAction(a)
  gs.Print()
  for _ in xrange(5):
    gs.AdvanceTurn()
    gs.Print()

  a = a_app.CreateApp(gs)
  gs.SetCurrentAction(a)
  gs.Print()

  for _ in xrange(10):
    gs.AdvanceTurn()
    gs.Print()


if __name__ == '__main__':
  main()
