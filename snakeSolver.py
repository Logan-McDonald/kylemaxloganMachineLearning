from snake import Game
from random import randint
import numpy as np
from keras.models import Sequential
from keras.optimizers import Adam
from keras.layers import Dense
from keras.models import load_model
import math,time,random

class NeuralNet:

    def __init__(self,x=15,y=15,filename='snake_model',train_games=100000,test_games=60,max_steps=50,gui=False):
        self.filename=filename
        self.inputs=7
        self.x=x
        self.y=y
        self.gui=gui
        self.train_games=train_games
        self.test_games=test_games
        self.max_steps=max_steps
        self.dirs={
            'left':0,
            'up':1,
            'right':2,
            'down':3
        }

    def getTrainingData(self):
        print('Getting Training Data . . .')
        data=[]
        number=int(self.train_games/20)
        for x in range(self.train_games):
            game=Game(x=self.x,y=self.y)
            c_data=[]
            self.game=game
            snake=game.start()
            current_state=self.getState(snake)
            for _ in range(self.max_steps):
                action=self.getAction()
                length=snake.length
                done,snake,closer=game.step(action)
                if done:break
                elif not closer:continue
                else:
                    correct_output=[0,0,0]
                    correct_output[action+1]=1
                    num=1
                    if snake.length>length:num=3
                    for _ in range(num):
                        c_data.append([current_state,correct_output])
                    current_state=self.getState(snake)
            if snake.length>2:
                for el in c_data:data.append(el)
            if x%number==0:print(f'{int(x/self.train_games*100)}%')
        return data

    def test(self,model):
        print('Testing . . .')
        num=int(self.test_games/20)
        lengths=[]
        game=Game(x=self.x,y=self.y)
        self.game=game
        for x in range(self.test_games):
            snake=game.start()
            steps=self.max_steps
            current_state=self.getState(snake)
            while True:
                m=model.predict(np.array([current_state]))
                action=list(m[0]).index(max(list(m[0])))-1
                length=snake.length
                done,snake,_=game.step(action)
                if done:break
                elif snake.length>length:steps=self.max_steps
                else:current_state=self.getState(snake)
                steps-=1
                if steps==0:
                    break
            lengths.append(snake.length)
            if x%num==0:print(f'{int((x/self.test_games)*100)}%')
        print(f'Average: {sum(lengths)/len(lengths)}')

    def blocked(self,snake,direction):
        point=(snake.x,snake.y)
        if direction=='up':point=(snake.x,snake.y-1)
        elif direction=='down':point=(snake.x,snake.y+1)
        elif direction=='left':point=(snake.x-1,snake.y)
        elif direction=='right':point=(snake.x+1,snake.y)
        return point in snake.body or point[0]<0 or point[1]<0 or point[0]>=self.x or point[1]>=self.y

    def trainModel(self,data,model):
        x_data=np.array([i[0] for i in data]).reshape(-1,self.inputs)
        y_data=np.array([i[1] for i in data]).reshape(-1,3)
        model.fit(x_data,y_data,epochs=10,shuffle=True)
        model.save(self.filename)
        return model

    def getSnakeDirection(self,snake):
        snake.dir

    def turnLeft(self,snake):
        new_dir=self.dirs[snake.dir]-1
        if new_dir==-1:a=3
        for d in self.dirs:
            if self.dirs[d]==new_dir:
                return d

    def turnRight(self,snake):
        new_dir=self.dirs[snake.dir]+1
        if new_dir==4:a=0
        for d in self.dirs:
            if self.dirs[d]==new_dir:
                return d

    def model(self):
        model=Sequential()
        model.add(Dense(5,input_shape=((self.inputs,)),activation='relu'))
        model.add(Dense(15))
        model.add(Dense(3,activation='sigmoid'))
        model.compile(loss='mean_squared_error',optimizer='adam',metrics=['mean_squared_error'])
        return model

    def getAction(self):
        return randint(-1,1)
    
    def getState(self,snake):
        direction=self.getSnakeDirection(snake)
        left=self.blocked(snake,self.turnLeft(snake))
        front=self.blocked(snake,direction)
        right=self.blocked(snake,self.turnRight(snake))
        applex_pos=self.game.apple[0]-snake.x
        appley_pos=self.game.apple[1]-snake.y
        return np.array([int(left),int(front),int(right),self.dirs[snake.dir],applex_pos,appley_pos,snake.length])

    def train(self):
        data=self.getTrainingData()
        snake_model=self.model()
        snake_model=self.trainModel(data,snake_model)
        self.test(snake_model)
        self.visualise()

    def visualise(self):
        self.showGame(self.loadModel())

    def showGame(self, model):
        game=Game(x=self.x,y=self.y,gui=True)
        self.game=game
        while True:
            snake=game.start()
            steps=self.max_steps
            current_state=self.getState(snake)
            while True:
                m=model.predict(np.array([current_state]))
                action=list(m[0]).index(max(list(m[0])))-1
                length=snake.length
                done,snake,c=game.step(action)
                if done:break
                elif snake.length>length:steps=self.max_steps
                else:current_state=self.getState(snake)
                time.sleep(.05)
                steps-=1
                if steps==0:
                    break

    def loadModel(self):
        return load_model(self.filename)

def main():
    NeuralNet(15,15).train()

if __name__=='__main__':
    main()