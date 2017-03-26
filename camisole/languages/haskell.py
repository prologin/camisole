from camisole.models import Lang, Program


class Haskell(Lang):
    source_ext = '.hs'
    compiler = Program('ghc', opts=['-dynamic', '-O2'])
    reference_source = r'module Main where main = putStrLn "42"'
