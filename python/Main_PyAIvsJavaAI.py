import sys
from time import sleep
from py4j.java_gateway import JavaGateway, GatewayParameters, CallbackServerParameters, get_field
#from WinOrGoHome import WinOrGoHome
from KickAIModify import KickAI
from DisplayInfo import DisplayInfo
from macheteModify import Machete
from WinOrGoHomeModify import WinOrGoHome

def check_args(args):
	for i in range(argc):
		if args[i] == "-n" or args[i] == "--n" or args[i] == "--number":
			global GAME_NUM
			GAME_NUM = int(args[i+1])

def start_game():
	manager.registerAI("WinOrGoHome", KickAI(gateway))
	print("Start game")
	game = manager.createGame("ZEN", "ZEN", "WinOrGoHome", "MctsAi", GAME_NUM)
	manager.runGame(game)
	
	print("After game")
	sys.stdout.flush()

def close_gateway():
	gateway.close_callback_server()
	gateway.close()

def main_process():
	check_args(args)
	start_game()
	close_gateway()


args = sys.argv
argc = len(args)
GAME_NUM = 1
gateway = JavaGateway(gateway_parameters=GatewayParameters(port=4242), callback_server_parameters=CallbackServerParameters());
manager = gateway.entry_point

main_process()

