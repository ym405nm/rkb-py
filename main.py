# coding=utf-8
import glob
import csv
from color import Color
import statistics
import re
import requests
from bs4 import BeautifulSoup
import time


class RKB:

    def __init__(self):
        self.race_number = ''
        self.players_count = 0
        self.race_title = ''
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
        # 結果の配列を用意する
        column_counter = 0
        for current_column in self.column_names:
            self.calc_result[current_column] = {}
            for i in range(1, self.players_count + 1):
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
                        add_parameter = float(0.7)
                    else:
                        add_parameter = float(0.9)
                elif collect_rate > 80:
                    add_parameter = float(1.2)
                self.calc_result[current_column]['player_' + selected_player.zfill(2)] += add_parameter
            column_counter += 1

    def view_result(self):
        print(self.race_title)
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
            for i in range(1, self.players_count + 1):
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

    def get_url_parse(self, url):
        if "https://my.keiba.rakuten.co.jp/" not in url:
            print("INVALID URL")
            exit()
        if re.search(r'/p/[0-9]{0,3}$', url):
            url = url.split("/p/")[0]
        if re.search(r'/sort/3$', url) is None:
            url = url.split("/sort")[0]
            url += "/sort/3"
        return url

    def get_page(self, url):
        urls = [
            url,
            url + "/p/2",
            url + "/p/3"
        ]
        player_count_flag = False
        for url_unit in urls :
            print("waiting...")
            time.sleep(3)
            print("Access to %s ..." % url_unit)
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
            headers = {'User-Agent': ua}
            response = requests.get(url_unit, headers=headers)
            bs = BeautifulSoup(response.text, "html.parser")
            table = bs.select_one("table.cellspacing0 tbody")
            rows = table.findAll("tr")
            for row in rows:
                tds = row.findAll("td")
                if player_count_flag is False: # 1ページめだけにやること
                    # レース名取得
                    race_title = bs.select_one("title").text
                    race_title = race_title.split(" |")[0]
                    self.race_title = race_title
                    players_url_soup = BeautifulSoup(str(tds[5]), 'html.parser')
                    players_url = players_url_soup.select_one("a").get('href')
                    self.get_player_number(players_url)
                    player_count_flag = True
                data_unit = [
                    tds[1].text,
                    tds[2].text,
                    tds[3].text,
                    tds[4].text,
                    tds[8].text,
                    tds[9].text
                ]
                self.data_list.append(data_unit)

    def get_player_number(self, player_url):
        print("waiting...")
        time.sleep(3)
        print("Access to %s ..." % player_url)
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
        headers = {'User-Agent': ua}
        response = requests.get(player_url, headers=headers)
        bs = BeautifulSoup(response.text, "html.parser")
        table = bs.select_one("table.orderTableStyle tbody")
        rows = table.findAll("tr")
        player_count = ''
        for row in rows:
            tds = row.findAll("td")
            if len(tds) > 2:
                player_box = tds[1].text
                player_count = player_box
        self.players_count = int(player_count)


if __name__ == '__main__':
    print("Plz URL")
    rkb = RKB()
    read_url = input()
    read_url = rkb.get_url_parse(read_url)
    print("URL %s OK? [y]" % read_url)
    url_ok = input()
    if "y" == url_ok:
        rkb.get_page(read_url)
        rkb.calc_start()
        rkb.view_result()

