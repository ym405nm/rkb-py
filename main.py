# coding=utf-8
import glob
import csv
from color import Color
import statistics


class RKB:

    def __init__(self, pc):
        self.players_count = pc
        self.data_list = []
        self.column_names = ["0_honmei", "1_taikou", "2_kuro", "3_shiro"]
        self.calc_result = {}
        self.big_stddev = 20  # 標準偏差をこれを超えると色を変える
        self.small_stddev = 10  # 標準偏差をこれを超えると色を変える
        self.ana_stddev = 10  # 穴をこれをさがると色を変える
        self.big_player = 40  # 予想数がこれを超えると色を変える
        self.small_player = 10  # 予想数がこれを超えると色を変える
        self.ana_player = 20  # 穴がこれだけ超えると要注意

    def calc_start(self):
        # データを読み込む
        dir_name = './input_data/*'
        files = glob.glob(dir_name)
        for csv_file in files:
            with open(csv_file) as f:
                reader = csv.reader(f)
                for row in reader:
                    self.data_list.append(row)
        if len(self.data_list) < 1:
            print('NO INPUT DATA')
            exit(0)
        # 結果の配列を用意する
        column_counter = 0
        for current_column in self.column_names:
            self.calc_result[current_column] = {}
            for i in range(1, players_count + 1):
                self.calc_result[current_column]['player_' + str(i).zfill(2)] = float(0)
            # データをマッピングしていく
            for data_unit in self.data_list:
                selected_player = data_unit[column_counter]
                add_parameter = float(1)
                # 回収率 によって変更していく
                hit_rate = float(data_unit[4].split('%')[0])
                collect_rate = float(data_unit[5].split('%')[0])
                if collect_rate > 100:  # 100以上は低く見積もる
                    if hit_rate < 50:
                        add_parameter = float(0.5)
                    else:
                        add_parameter = float(0.9)
                elif collect_rate > 80:
                    add_parameter = float(1.2)
                self.calc_result[current_column]['player_' + selected_player.zfill(2)] += add_parameter
            column_counter += 1

    def view_result(self):
        for column_name in self.column_names:  # カラムごとのループ
            column_statics = self.get_column_statics(column_name)
            column_stddev = column_statics["stddev"]  # 標準偏差
            if column_stddev < self.small_stddev:
                column_stddev = Color.RED + str(column_statics["stddev"]) + Color.RESET
            elif column_stddev > self.big_stddev:
                column_stddev = Color.BG_GREEN + str(column_statics["stddev"]) + Color.RESET
            else:
                column_stddev = str(column_stddev)
            column_line = "%s (stddev: %s)" % (
                column_name.split("_")[1],  # カラム名
                column_stddev  # 標準偏差
            )
            print(column_line)
            for i in range(1, players_count + 1):
                player_data = 'player_' + str(i).zfill(2)
                player_count = self.calc_result[column_name][player_data]
                player_count = int(player_count)
                player_percent = int(100 * float(player_count) / column_statics["sum"])
                asterisk_text = ""
                asterisk_count = 0
                while asterisk_count < player_percent:
                    asterisk_text += "*"
                    asterisk_count += 1
                if "ro" in column_name and player_percent > self.ana_player:
                    player_percent = Color.BG_RED + str(player_percent) + Color.RESET
                elif player_percent > self.big_player:  # 予想数に応じて色をかえる
                    player_percent = Color.BG_GREEN + str(player_percent) + Color.RESET
                elif player_percent < self.small_player:
                    player_percent = Color.BLUE + str(player_percent) + Color.RESET
                else:
                    player_percent = str(player_percent)
                view_line = "%s: %s ( %s )" % (
                    player_data,
                    asterisk_text,
                    player_percent)
                print(view_line)

    def get_column_statics(self, column_name):
        result_sum = float(0)
        data_array = []
        for player_name in self.calc_result[column_name]:
            result_sum += self.calc_result[column_name][player_name]
            data_array.append(self.calc_result[column_name][player_name])
        return {
            "sum": result_sum,
            "stddev": statistics.stdev(data_array)
        }


if __name__ == '__main__':
    print("HOW MANY PLAYERS?")
    players_count = int(input())
    rkb = RKB(players_count)
    # 初期設定
    rkb.calc_start()
    # 結果描写
    rkb.view_result()
