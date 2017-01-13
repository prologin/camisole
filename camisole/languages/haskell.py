from camisole.models import Lang


class Haskell(Lang):
    source_ext = '.hs'
    compiler = '/usr/bin/ghc'
    compile_opts = ['-dynamic', '-O2']
    reference_source = r'module Main where main = putStrLn "42"'
