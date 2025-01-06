from Chessnut import Game

PIECE_VALUES = {
    "P": 1,  # ポーン
    "N": 3,  # ナイト
    "B": 3,  # ビショップ
    "R": 5,  # ルーク
    "Q": 9,  # クイーン
    "K": 50,  # キング
}

# 0:Normal, 1:Check
END_STATUS_VALUES = [
    2, # Checkmate
    3, # Stalemate
]


# 評価関数
def evaluate(game, is_white):
    """
    PIECE_VALUESに基づいて現在の盤面スコアを計算する
    """
    board = game.board
    score = 0

    for square in range(64):
        piece = board.get_piece(square)
        if piece == " ":
            continue
        value = PIECE_VALUES[piece.upper()]
        if piece.isupper() == is_white:  # 白の駒
            score += value
        else:  # 黒の駒
            score -= value

    return score


# alpha-beta 枝刈り
def alpha_beta(game, depth, alpha, beta, is_maximizing):
    """
    alpha-beta枝刈りを用いて最適な評価値を計算する

    Args:
        - is_maximizin(bool): 白駒ならTrue,黒駒ならFalse
    """
    if depth == 0 or game.status in END_STATUS_VALUES:
        return evaluate(game, is_maximizing)

    # 合法手を取得
    moves = list(game.get_moves())

    if is_maximizing:
        value = float("-inf")
        for move in moves:
            sim_game = Game(str(game))
            sim_game.apply_move(move)
            evaluation = alpha_beta(
                game=sim_game, depth=depth - 1, alpha=alpha, beta=beta, is_maximizing=is_maximizing
            )
            value = max(value, evaluation)
            alpha = max(alpha, value)
            if alpha >= beta:  # 枝刈り条件
                break
        return value
    else:
        value = float("inf")
        for move in moves:
            sim_game = Game(str(game))
            sim_game.apply_move(move)
            evaluation = alpha_beta(
                game=sim_game, depth=depth - 1, alpha=alpha, beta=beta, is_maximizing=is_maximizing
            )
            value = min(value, evaluation)
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value


def chess_bot(obs):
    # ゲームの情報の取得
    game = Game(obs.board)
    is_white = obs.mark == "white"
    moves = list(game.get_moves())

    best_move = None
    best_value = float("-inf") if is_white else float("inf")

    # Alpha-Beta法で最適な手を探索
    for move in moves:
        sim_game = Game(str(game))
        sim_game.apply_move(move)
        value = alpha_beta(
            sim_game, depth=1, alpha=float("-inf"), beta=float("inf"), is_maximizing=is_white
        )

        if is_white:
            if value > best_value:
                best_value = value
                best_move = move
        else:
            if value < best_value:
                best_value = value
                best_move = move

    return best_move
