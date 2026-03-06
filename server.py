from openreward.environments import Server
from env import CrosswordsEnvironment

if __name__ == "__main__":
    server = Server([CrosswordsEnvironment])
    server.run()
