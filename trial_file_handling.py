score = input("Enter a score: ")
text = input("Enter your three letter name: ")

f = open("leaderboard.txt", "a")
f.write("Score: {} - Player: {} \n".format(score, text))
f.close()

#open and read the file after the appending:
f = open('leaderboard.txt').readlines()
f.sort()
f.reverse()
for i in range(5):
    print(f[i])