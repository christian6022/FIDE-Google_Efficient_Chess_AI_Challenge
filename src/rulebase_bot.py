import random

from Chessnut import Game

PIECE_VALUES = {
    "P": 1,  # ポーン
    "N": 3,  # ナイト
    "B": 3,  # ビショップ
    "R": 5,  # ルーク
    "Q": 9,  # クイーン
    "K": 0,  # キング
}

ENEMY_SCORE = 39


def chess_bot(obs):
    """
    優先順位
        0. 盤面情報の取得
            ・先手・後手の判定
            ・合法的な一手の取得
            ・相手の点数の取得
        1.0 キャスリング
        1. ✅チェックメイト
        2. 駒の捕獲（駒の優先順位あり）
        3. フォーク・ピン・スキュアの判定（回避優先）
        4. センターエリアの確保
        4. クイーンへの昇格
        5. ランダム
            ・ポーンチェーンの構築
            ・相手陣地に侵入


    引数:
        obs: 現在の盤面の状態をFEN文字列として表す'board'属性を持つオブジェクト

    戻り値:
        UCI表記（例:e2e4）で選択された手を表す文字列
    """

    def castling(game, is_white, curr_move_cnt):
        """
        白：イタリアンゲーム
        黒：シシリアン・ドラゴンディフェンス
        """
        white_moves = [
            "e2e4",  # ポーンを2マス進める
            "g1f3",  # ナイトを展開する
            "f1c4",  # ビショップを展開する
            "e1g1",  # キャスリング
        ]

        black_moves = [
            "e7e5",  # ポーンを2マス進める
            "d8e7",  # クイーンを展開する
            "b8c6",  # ナイトを展開する
            "d7d6",  # ポーンを1マス進める
            "c8g4",  # ビショップを展開する
            "d8c8",  # キャスリング
        ]
        # 現在の合法手を取得
        legal_moves = set(game.get_moves())

        # 白の手順
        if is_white:
            if curr_move_cnt <= len(white_moves):
                move = white_moves[curr_move_cnt - 1]
                if move in legal_moves:  # 合法手か確認
                    return move
        # 黒の手順
        else:
            if curr_move_cnt <= len(black_moves):
                move = black_moves[curr_move_cnt - 1]
                if move in legal_moves:  # 合法手か確認
                    return move

        # 指定された手が合法でない場合はNoneを返す
        return None

    def strategy_endgame(game, moves, is_white, fifty_rule_cnt):
        # ポーンの識別（白: "P", 黒: "p"）
        porn_piece = "P" if is_white else "p"

        # ポーンがいる場合、ポーンの手を取得
        has_porn = any(game.board.get_piece(square) == porn_piece for square in range(64))
        if has_porn:
            porn_moves = [
                move for move in moves if game.board.get_piece(Game.xy2i(move[:2])) == porn_piece
            ]

        if fifty_rule_cnt > 40 and has_porn:
            for _ in range(len(porn_moves)):
                move = random.choice(porn_moves)
                if not is_move_capturable(game, move, is_white):
                    return move

        while True:
            move = random.choice(moves)
            if not is_move_capturable(game, move, is_white):
                return move

    def calculate_piece_score(fen, is_white):
        """
        FEN文字列に基づいて駒のスコアを計算する。
        自分の駒（is_white=Trueなら大文字、Falseなら小文字）を計算する。

        引数:
            fen (str): FEN文字列。
            is_white (bool): Trueなら白のスコア、Falseなら黒のスコアを計算。

        戻り値:
            int: 駒の合計スコア。
        """
        # ボード情報を抽出（FENの最初のフィールド）
        board_state = fen.split()[0]

        # 駒を走査してスコアを計算
        total_score = 0
        for char in board_state:
            if char.isalpha():
                if is_white and char.islower():
                    char = char.upper()
                    total_score += PIECE_VALUES[char]
                elif (not is_white) and char.isupper():
                    char = char.lower()
                    total_score += PIECE_VALUES[char.upper()]

        return total_score

    def is_move_capturable(game, move, is_white):
        """
        指定されたmoveが次の相手の手で取られるかを判定する。

        引数:
            game: 現在の盤面オブジェクト。
            move (str): UCI表記の手（例: "e2e4"）。
            is_white (bool): 自分が白（True）か黒（False）か。

        戻り値:
            bool: 次の相手の一手で駒が取られる可能性がある場合True、そうでなければFalse。
        """
        # 現在のゲーム状態をコピー
        sim_game = Game(str(game))

        # 指定されたmoveを適用
        sim_game.apply_move(move)

        # 自分の駒の位置（行き先のマス）を取得
        target_square = move[2:4]  # 行き先の座標

        # 次の相手の合法手を取得
        opponent_moves = list(sim_game.get_moves())

        # 相手の手で取られるかチェック
        for opponent_move in opponent_moves:
            if opponent_move[2:4] == target_square:  # 行き先が自分の駒の位置
                return True

        return False

    ## 0. 盤面情報の取得
    # 先手・後手の判定
    is_white = obs.mark == "white"

    # 合法的な一手を全て取得
    game = Game(obs.board)
    moves = list(game.get_moves())
    fen = obs.board
    curr_move_cnt = int(fen.split(" ")[-1])
    fifty_rule_cnt = int(fen.split(" ")[-2])

    # 相手の点数の取得
    enemy_score = calculate_piece_score(fen, is_white)

    # 1-0. キャスリング
    if curr_move_cnt < 7:
        move = castling(game, is_white, curr_move_cnt)
        if move is not None:
            return move

    # 1. チェックメイト
    for move in moves[:10]:
        g = Game(obs.board)
        g.apply_move(move)
        if g.status == Game.CHECKMATE:
            return move

    # 2. 駒の捕獲
    """
    ・相手駒を捕獲できる場合は捕獲
    ・捕獲後に、相手に捕獲されてしまう場合は、コマの損得で判断
    """
    for move in moves:
        # 特定のマスに駒が存在する場合、その駒の種類を取得
        opponent_piece = game.board.get_piece(Game.xy2i(move[2:4]))
        opponent_piece = opponent_piece.upper() if is_white else opponent_piece

        mine_piece = game.board.get_piece(Game.xy2i(move[:2]))

        if opponent_piece != " ":
            # 次の一手で取られるか、自分の駒、相手の駒を取得
            is_capturable = is_move_capturable(game, move, is_white)
            if not is_capturable:  # 次の一手で取られない場合、その手を選択
                return move
            else:  # 次の一手で取られる場合、コマの損得で判断
                if mine_piece == "Q":
                    continue
                elif PIECE_VALUES[mine_piece.upper()] < PIECE_VALUES[opponent_piece.upper()]:
                    return move
                else:
                    continue

    # 3. クイーンへの昇格
    for move in moves:
        if "q" in move.lower():
            return move

    if enemy_score > 10:
        # 4. ランダムに次の一手を選択
        while True:
            move = random.choice(moves)
            if not is_move_capturable(game, move, is_white):
                return move
    else:
        return strategy_endgame(game, moves, is_white, fifty_rule_cnt)
