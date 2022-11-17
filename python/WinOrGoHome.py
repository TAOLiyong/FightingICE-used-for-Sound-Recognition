import collections
import time

import os
import pickle

import numpy as np
import py4j.java_gateway


class Agent:
    class Linear:
        def __init__(self, weight, bias):
            self.weight = weight
            self.bias = bias

        def __call__(self, x):
            x = np.dot(self.weight, x)
            x = x + self.bias
            return x

    def __init__(self, state_dict):
        self.pi0 = self.Linear(state_dict["_linear.0.weight"], state_dict["_linear.0.bias"])
        self.pi2 = self.Linear(state_dict["_linear.2.weight"], state_dict["_linear.2.bias"])
        self.pi4 = self.Linear(state_dict["_linear.4.weight"], state_dict["_linear.4.bias"])

    @staticmethod
    def relu(x):
        return np.maximum(0, x)

    @staticmethod
    def softmax(x, dim):
        return np.exp(x) / np.sum(np.exp(x), axis=dim,)

    def infer(self, x):
        x = self.relu(self.pi0(x))
        x = self.relu(self.pi2(x))
        x = self.pi4(x)
        action = np.argmax(x)
        return action


class WinOrGoHome(object):
    def __init__(self, gateway):
        self.gateway = gateway
        self.para_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'WinOrGoHome')

        self.obs = None
        self.just_inited = True
        self._actions = "AIR_A AIR_B AIR_D_DB_BA AIR_D_DB_BB AIR_D_DF_FA AIR_D_DF_FB AIR_DA AIR_DB AIR_F_D_DFA AIR_F_D_DFB AIR_FA AIR_FB AIR_GUARD AIR_UA AIR_UB BACK_JUMP BACK_STEP CROUCH_A CROUCH_B CROUCH_FA CROUCH_FB CROUCH_GUARD DASH FOR_JUMP FORWARD_WALK JUMP STAND_A STAND_B STAND_D_DB_BA STAND_D_DB_BB STAND_D_DF_FA STAND_D_DF_FB STAND_D_DF_FC STAND_F_D_DFA STAND_F_D_DFB STAND_FA STAND_FB STAND_GUARD THROW_A THROW_B NEUTRAL AIR"
        self.action_strs = self._actions.split(" ")

        _origin_actions = "AIR AIR_A AIR_B AIR_D_DB_BA AIR_D_DB_BB AIR_D_DF_FA AIR_D_DF_FB AIR_DA AIR_DB AIR_F_D_DFA AIR_F_D_DFB AIR_FA AIR_FB AIR_GUARD AIR_GUARD_RECOV AIR_RECOV AIR_UA AIR_UB BACK_JUMP BACK_STEP CHANGE_DOWN CROUCH CROUCH_A CROUCH_B CROUCH_FA CROUCH_FB CROUCH_GUARD CROUCH_GUARD_RECOV CROUCH_RECOV DASH DOWN FOR_JUMP FORWARD_WALK JUMP LANDING NEUTRAL RISE STAND STAND_A STAND_B STAND_D_DB_BA STAND_D_DB_BB STAND_D_DF_FA STAND_D_DF_FB STAND_D_DF_FC STAND_F_D_DFA STAND_F_D_DFB STAND_FA STAND_FB STAND_GUARD STAND_GUARD_RECOV STAND_RECOV THROW_A THROW_B THROW_HIT THROW_SUFFER"
        self.origin_action_strs = _origin_actions.split(" ")

    def close(self):
        pass

    def initialize(self, gameData, player):
        self.oppActionCounter = collections.defaultdict(int)
        self.lastOppAction = None

        self.inputKey = self.gateway.jvm.struct.Key()
        self.frameData = self.gateway.jvm.struct.FrameData()
        self.cc = self.gateway.jvm.aiinterface.CommandCenter()

        self.player = player
        self.gameData = gameData

        self.charaname = str(gameData.getCharacterName(self.player))
        self.oppoAIname = str(gameData.getAiName(not self.player))

        if self.charaname == "ZEN":
            if self.oppoAIname == "MctsAi":
                print('as zen vs mcts')
                self.action_strs = self.origin_action_strs
                filename = 'zen_mcts.pkl'
            else:
                print('as zen vs general')
                filename = ['zen_general_air.pkl', 'zen_general_ground.pkl']
        elif self.charaname == "LUD":
            if self.oppoAIname == "MctsAi":
                print('as lud vs mcts')
                filename = 'lud_mcts.pkl'
            else:
                print('as lud vs general')
                filename = 'lud_general.pkl'
        elif self.charaname == "GARNET":
            if self.oppoAIname == "MctsAi":
                print('as garnet vs mcts')
                filename = 'garnet_mcts.pkl'
            else:
                print('as garnet vs general')
                filename = 'garnet_general.pkl'
        else:
            print("Warning: Unexpected character!!!")
            filename = 'zen_general_ground.pkl'

        if isinstance(filename, str):
            with open(os.path.join(self.para_folder, filename), "rb") as f:
                state_dict = pickle.load(f)
            self.model = Agent(state_dict)
        else:
            with open(os.path.join(self.para_folder, filename[0]), "rb") as f:
                state_dict = pickle.load(f)
            self.model_air = Agent(state_dict)
            with open(os.path.join(self.para_folder, filename[1]), "rb") as f:
                state_dict = pickle.load(f)
            self.model_ground = Agent(state_dict)

        self.isGameJustStarted = True
        self.last_5_oppo_posX = collections.deque(maxlen=5)
        self.last_10_oppo_hp = collections.deque(maxlen=10)

        return 0

    def roundEnd(self, x, y, z):
        self.just_inited = True
        self.obs = None
        self.oppActionCounter = collections.defaultdict(int)
        self.lastOppAction = None
        self.last_5_oppo_posX = collections.deque(maxlen=5)
        self.last_10_oppo_hp = collections.deque(maxlen=10)

    def getScreenData(self, sd):
        pass

    def getAudioData(self, ad):
        pass

    def getInformation(self, frameData, isControl):
        self.frameData = frameData
        self.isControl = isControl
        
        print(1)
        try:
            opp = self.frameData.getCharacter(not self.player)
            oppAction = opp.getAction().ordinal()
            print(2)
            if self.lastOppAction is not None and oppAction != self.lastOppAction:
                self.oppActionCounter[oppAction] += 1
            self.lastOppAction = oppAction
            print(3)
        except:
            pass
        print(4)
        self.cc.setFrameData(self.frameData, self.player)
        if frameData.getEmptyFlag():
            return

    def input(self):
        return self.inputKey

    def gameEnd(self):
        pass

    def processing(self):
        if self.frameData.getEmptyFlag() or self.frameData.getRemainingTime() <= 0:
            self.isGameJustStarted = True
            return

        if self.cc.getSkillFlag():
            self.inputKey = self.cc.getSkillKey()
            return

        if not self.isControl:
            return

        self.inputKey.empty()
        self.cc.skillCancel()

        if self.just_inited:
            self.just_inited = False
        self.obs = self.get_obs()

        if self.charaname == 'ZEN' and self.oppoAIname != 'MctsAi':
            my = self.frameData.getCharacter(self.player)
            opp = self.frameData.getCharacter(not self.player)
            if my.getHp() > 150:
                action = self.model_air.infer(self.obs)
            else:
                action = self.model_ground.infer(self.obs)
        else:
            action = self.model.infer(self.obs)
        str_action = self.action_strs[action]
        str_action = self.force_act(str_action)
        self.cc.commandCall(str_action)

    def get_obs(self):
        my = self.frameData.getCharacter(self.player)
        opp = self.frameData.getCharacter(not self.player)

        myHp = my.getHp() / 400
        myEnergy = my.getEnergy() / 300
        myLeft = (my.getLeft() - 480) / 960
        myRight = (my.getRight() - 480) / 960
        myX = (myLeft + myRight) / 2
        myBottom = (my.getBottom() - 320) / 640
        myTop = (my.getTop() - 320) / 640
        myY = (myBottom + myTop) / 2
        mySpeedX = my.getSpeedX() / 15
        mySpeedY = my.getSpeedY() / 28
        myHits = my.getHitCount() / 10
        myState = my.getAction().ordinal()
        myRemainingFrame = my.getRemainingFrame() / 70

        oppHp = opp.getHp() / 400
        oppEnergy = opp.getEnergy() / 300
        oppLeft = (opp.getLeft() - 480) / 960
        oppRight = (opp.getRight() - 480) / 960
        oppX = (oppLeft + oppRight) / 2
        oppBottom = (opp.getBottom() - 320) / 640
        oppTop = (opp.getTop() - 320) / 640
        oppY = (oppBottom + oppTop) / 2
        oppSpeedX = opp.getSpeedX() / 15
        oppSpeedY = opp.getSpeedY() / 28
        oppHits = opp.getHitCount() / 10
        oppState = opp.getAction().ordinal()
        oppRemainingFrame = opp.getRemainingFrame() / 70

        diffHp = oppHp - myHp
        diffX = oppX - myX
        diffY = oppY - myY
        diffSpeedX = oppSpeedX - mySpeedX
        diffSpeedY = oppSpeedY - mySpeedY

        game_frame_num = self.frameData.getFramesNumber() / 3600

        observation = []

        observation.append(myHp)
        observation.append(myEnergy)
        observation.append(myLeft)
        observation.append(myRight)
        observation.append(myX)
        observation.append(myBottom)
        observation.append(myTop)
        observation.append(myY)
        if mySpeedX < 0:
            observation.append(0)
        else:
            observation.append(1)
        observation.append(mySpeedX)
        if mySpeedY < 0:
            observation.append(0)
        else:
            observation.append(1)
        observation.append(mySpeedY)
        observation.append(myHits)
        for i in range(56):
            if i == myState:
                observation.append(1)
            else:
                observation.append(0)
        observation.append(myRemainingFrame)

        observation.append(oppHp)
        observation.append(oppEnergy)
        observation.append(oppLeft)
        observation.append(oppRight)
        observation.append(oppX)
        observation.append(oppBottom)
        observation.append(oppTop)
        observation.append(oppY)
        if oppSpeedX < 0:
            observation.append(0)
        else:
            observation.append(1)
        observation.append(oppSpeedX)
        if oppSpeedY < 0:
            observation.append(0)
        else:
            observation.append(1)
        observation.append(oppSpeedY)
        observation.append(oppHits)
        for i in range(56):
            if i == oppState:
                observation.append(1)
            else:
                observation.append(0)
        observation.append(oppRemainingFrame)

        observation.append(diffHp)
        observation.append(diffX)
        observation.append(diffY)
        observation.append(diffSpeedX)
        observation.append(diffSpeedY)

        observation.append(game_frame_num)

        def helper(proj, idx):
            hitSpeedX = proj[idx].getSpeedX() / 15.
            hitSpeedY = proj[idx].getSpeedY() / 28.
            hitStartUp = proj[idx].getStartUp() / 360.
            hitActive = proj[idx].getActive() / 360.
            hitGuardDamage = proj[idx].getGuardDamage() / 50.
            hitStartAddEnergy = proj[idx].getStartAddEnergy() / 50.
            hitHitAddEnergy = proj[idx].getHitAddEnergy() / 50.
            hitGuardAddEnergy = proj[idx].getGuardAddEnergy() / 50.
            hitGiveEnergy = proj[idx].getGiveEnergy() / 50.
            hitImpactX = proj[idx].getImpactX() / 40.
            hitImpactY = proj[idx].getImpactY() / 15.
            hitGiveGuardRecov = proj[idx].getGiveGuardRecov() / 60.
            hitCanPushDown = 1. if proj[idx].isDownProp() else 0.
            hitDamage = proj[idx].getHitDamage() / 200.0
            hitAreaNowLeft = (proj[idx].getCurrentHitArea().getLeft() - 480) / 960.0
            hitAreaNowRight = (proj[idx].getCurrentHitArea().getRight() - 480) / 960.0
            hitAreaNowX = ((proj[idx].getCurrentHitArea().getLeft() + proj[idx].getCurrentHitArea().getRight()) / 2 - 480) / 960.0
            hitAreaNowTop = (proj[idx].getCurrentHitArea().getTop() - 320) / 640.0
            hitAreaNowBottom = (proj[idx].getCurrentHitArea().getBottom() - 320) / 640.0
            hitAreaNowY = ((proj[idx].getCurrentHitArea().getTop() + proj[idx].getCurrentHitArea().getBottom()) / 2 - 320) / 640.0
            observation.append(hitSpeedX)
            observation.append(hitSpeedY)
            observation.append(hitStartUp)
            observation.append(hitActive)
            observation.append(hitGuardDamage)
            observation.append(hitStartAddEnergy)
            observation.append(hitHitAddEnergy)
            observation.append(hitGuardAddEnergy)
            observation.append(hitGiveEnergy)
            observation.append(hitImpactX)
            observation.append(hitImpactY)
            observation.append(hitGiveGuardRecov)
            observation.append(hitCanPushDown)
            observation.append(hitDamage)
            observation.append(hitAreaNowLeft)
            observation.append(hitAreaNowRight)
            observation.append(hitAreaNowX)
            observation.append(hitAreaNowTop)
            observation.append(hitAreaNowBottom)
            observation.append(hitAreaNowY)

        myProjectiles = self.frameData.getProjectilesByP1()
        oppProjectiles = self.frameData.getProjectilesByP2()
        if not self.player:
            myProjectiles, oppProjectiles = oppProjectiles, myProjectiles

        if len(myProjectiles) == 2:
            helper(myProjectiles, 0)
            helper(myProjectiles, 1)
        elif len(myProjectiles) == 1:
            helper(myProjectiles, 0)
            for t in range(20):
                observation.append(0.0)
        else:
            for t in range(40):
                observation.append(0.0)

        if len(oppProjectiles) == 2:
            helper(oppProjectiles, 0)
            helper(oppProjectiles, 1)
        elif len(oppProjectiles) == 1:
            helper(oppProjectiles, 0)
            for t in range(20):
                observation.append(0.0)
        else:
            for t in range(40):
                observation.append(0.0)

        action_history = [0.] * 56
        n_past_action = sum(self.oppActionCounter.values())
        if n_past_action > 0:
            for action_id, count in self.oppActionCounter.items():
                action_history[action_id] = count / n_past_action
        observation.extend(action_history)

        observation = np.asarray(observation, dtype=np.float32)
        return observation

    def force_act(self, str_action):
        if str_action == 'STAND_GUARD':
            str_action = "4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4"
        elif str_action == 'CROUCH_GUARD':
            str_action = "1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1"

        my = self.frameData.getCharacter(self.player)
        opp = self.frameData.getCharacter(not self.player)
        oppMotionData = self.gameData.getMotionData(not self.player)
        oppState = opp.getAction().ordinal()
        oppAction = py4j.java_gateway.get_field(oppMotionData.get(oppState), 'actionName')
        oppProjectiles = self.frameData.getProjectilesByP2()

        diffX = abs(my.getCenterX() - opp.getCenterX())
        diffY = abs(my.getCenterY() - opp.getCenterY())
        self.last_5_oppo_posX.append(opp.getCenterX())
        self.last_10_oppo_hp.append(opp.getHp())

        # a heuristic counter to the popular GARNET trick "フェアプレー時代の終焉を告げる技"
        if self.charaname == 'GARNET':
            if oppAction == 'AIR_UB' and diffX < 150 and diffY < 50 and my.getRight() != 960 and my.getLeft() != 0:
                str_action = "4"

        # a patch aiming at the ZEN and GARNET's lazy player who has a brief lead currently
        if self.oppoAIname != 'MctsAi' and self.charaname != 'LUD':
            if diffX > 50 and my.getHp() <= opp.getHp() and len(oppProjectiles) == 0 and \
                    len(self.last_5_oppo_posX) == 5 and np.std(self.last_5_oppo_posX) == 0. and \
                    len(self.last_10_oppo_hp) == 10 and np.std(self.last_10_oppo_hp) == 0.:
                str_action = 'FORWARD_WALK'

        return str_action

    # This part is mandatory
    class Java:
        implements = ["aiinterface.AIInterface"]

