import random

from Chessnut import Game


def chess_bot(obs):
    """
    優先順位
        1. チェックメイト
        2. 駒の捕獲
        3. クイーンへの昇格
        4. ランダム

    引数:
        obs: 現在の盤面の状態をFEN文字列として表す'board'属性を持つオブジェクト

    戻り値:
        UCI表記（例:e2e4）で選択された手を表す文字列
    """
    # 0. 盤面情報を取得し、合法的な一手を全て取得
    game = Game(obs.board)
    moves = list(game.get_moves())

    # 1. チェックメイト
    for move in moves[:10]:
        g = Game(obs.board)
        g.apply_move(move)
        if g.status == Game.CHECKMATE:
            return move

    # 2. 駒の捕獲
    """
    UCI表記の3~4文字目が行き先のマス
    -> get_pieceで対象のマスに駒があるか確認
    ・' ': 何もない
    ・'P': 白ポーン
    ...
    """
    for move in moves:
        if game.board.get_piece(Game.xy2i(move[2:4])) != " ":
            return move

    # 3. クイーンへの昇格
    for move in moves:
        if "q" in move.lower():
            return move

    # 4. ランダムに次の一手を選択
    return random.choice(moves)
