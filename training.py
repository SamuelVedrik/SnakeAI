import SnakeAI
import Snake
import random

if __name__ == "__main__":

    CREATE_NEW = True
    generations = 20000
    PATH = "AI_2.csv"
    alpha = SnakeAI.AI()
    if not CREATE_NEW:
        alpha.load(PATH)
    else:
        alpha.random(1)

    alpha_game = Snake.SetTrainingSnake(alpha)
    alpha_game.play()
    alpha_score = alpha_game.score - alpha.genetic_weight()

    for i in range(generations):

        competitor = alpha.copy()
        mutation_epsilon = random.uniform(0.5, 1.5)
        competitor.mutate(mutation_epsilon)
        competitor_game = Snake.TrainingSnake(competitor)
        competitor_game.play()

        competitor_score = competitor_game.score - competitor.genetic_weight()

        if i % 200 == 0:
            print(f"{i} gen, A: {alpha_score}")
        if competitor_score > alpha_score:
            alpha = competitor
            alpha.save(PATH)
            alpha_score = competitor_score
            print(f"Evolution: {competitor_score}, with {competitor_game.score}"
                  f" game score and {competitor.genetic_weight()} genetic weight")
