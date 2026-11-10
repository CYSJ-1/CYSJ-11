#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《雨夜留声》—— 单文件命令行推理游戏。"""

import os
import sys


def _setup_console():
    """尽量让 Windows 控制台正确显示中文。"""
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        except Exception:
            pass
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


_setup_console()

WIDTH = 48
FW_DIGITS = str.maketrans("０１２３４５６７８９", "0123456789")


def rule(ch="─"):
    print(ch * WIDTH)


def header(title):
    print()
    rule("═")
    print(f"  {title}")
    rule("═")


def pause(prompt="  （按回车继续）"):
    try:
        input(prompt)
    except (EOFError, KeyboardInterrupt):
        print()
        raise SystemExit(0)


HINTS = [
    "先别急着找动机。先问：陆鸿声到底是什么时候死的？尸体不会说谎，但它所在的环境会。",
    "书房热得反常。高温会让尸冷变慢，顾行舟给出的死亡时间就会偏晚。再看死者手腕上的表——它停在 21:05。",
    "如果陆鸿声在 21:05 就死了，21:40 的枪声是从哪来的？留声机的唱针为什么停在收尾槽？那张唱片最后一段是什么？",
    "枪声是一张唱片。谁最熟悉陆鸿声的唱片，谁在 21:35 离开过客厅，谁又刚好穿着一件深红色开衫？",
    "凶手是沈青禾。她用《雷雨》音效盘伪造了 21:40 的枪声，让自己在牌桌旁获得不在场证明。去指认她，并选择“留声机唱片”和“腕表与闷响”。",
]


class Game:
    def __init__(self):
        self.clues = {}
        self.seen = set()
        self.hint_index = 0
        self.wrong = 0
        self.finished = False

        # 玩家一开始就知道的两件事。
        self.add_clue(
            "self_alibi",
            "21:40 枪响时，你、沈青禾、罗坤在客厅打牌；沈青禾坐在你对面。",
            "已知",
            quiet=True,
        )
        self.add_clue(
            "self_absence",
            "21:35 沈青禾说去拿披肩，离开约四分钟，回来时有些喘。",
            "已知",
            quiet=True,
        )

    # ------------------------------------------------------------------
    # 基础工具
    # ------------------------------------------------------------------
    def add_clue(self, key, text, category="现场", quiet=False):
        if key in self.clues:
            return False
        self.clues[key] = (category, text)
        if not quiet:
            print()
            print(f"  【新线索·{category}】{text}")
        return True

    def has(self, *keys):
        return all(k in self.clues for k in keys)

    def first(self, key):
        if key in self.seen:
            return False
        self.seen.add(key)
        return True

    def mark(self, key):
        return "  *" if key in self.seen else ""

    def quit_game(self):
        print()
        print("  你合上笔记本。雨还在下。")
        print("  天快亮了，但你没有说出答案。")
        print()
        raise SystemExit(0)

    def ask(self, prompt, valid):
        while True:
            try:
                raw = input(prompt)
            except (EOFError, KeyboardInterrupt):
                self.quit_game()

            raw = raw.strip().translate(FW_DIGITS)
            low = raw.lower()

            if low in ("q", "quit", "退出"):
                self.quit_game()
            if low in ("h", "hint", "提示"):
                self.show_hint()
                continue
            if low in ("n", "笔记", "线索"):
                self.notebook()
                continue
            if low in ("?", "help", "帮助"):
                print("  输入选项前的数字。n 笔记，a 指认，h 提示，q 退出。")
                continue
            if low in ("a", "指认", "推理") and "a" in valid:
                return "a"
            if low in valid:
                return low

            if not low:
                print("  输入一个选项。输入 h 获取提示，q 退出。")
            else:
                print("  没有这个选项。")

    def show_hint(self):
        if self.hint_index >= len(HINTS):
            print()
            print("  没有更多提示了。")
            return
        print()
        print(f"  【提示 {self.hint_index + 1}】{HINTS[self.hint_index]}")
        self.hint_index += 1
        pause()

    def notebook(self):
        header("笔记")
        if not self.clues:
            print("  笔记本还是空的。")
            pause()
            return

        order = ["已知", "现场", "时间", "人物", "动机"]
        index = 0
        for cat in order:
            items = [(k, v) for k, v in self.clues.items() if v[0] == cat]
            if not items:
                continue
            print(f"  【{cat}】")
            for _key, (_cat, text) in items:
                index += 1
                print(f"   {index:>2}. {text}")
            print()
        print(f"  共 {len(self.clues)} 条线索。")
        pause()

    # ------------------------------------------------------------------
    # 开场
    # ------------------------------------------------------------------
    def intro(self):
        header("雨 夜 留 声")
        print("              一桩山庄密室谋杀案")
        rule("─")
        print()
        print("  雨下了整整一夜。")
        print()
        print("  民国二十五年，江南。")
        print("  听雨山庄建在半山腰，只有一条石桥与外界相连。")
        print("  晚上八点五十分，雷声滚过山脊，桥那头的电线闪了闪，")
        print("  整座山庄陷入黑暗。九点十分，备用发电机响了起来，")
        print("  但电话线已经断了。")
        print()
        print("  九点以前，你一直待在自己的房间里看书。")
        print("  雨太大，你什么也没听见。")
        print()
        print("  九点半，你下楼时，沈青禾和罗坤已经在牌桌旁。")
        print("  九点三十五，沈青禾说去拿披肩，离开了四五分钟。")
        print("  九点四十，她刚坐下发牌，楼上就传来一声闷响。")
        print()
        print("  你们冲上楼。书房的门锁着，罗坤用肩膀撞开了它。")
        print("  壁炉里的火正旺，留声机还在转。")
        print("  陆鸿声倒在书桌和壁炉之间，左胸有一处枪伤。")
        print("  他左手腕上的表，停在九点零五分。")
        print()
        print("  九点五十五，你重新回到书房。")
        print("  警察最早也要天亮才能上山。")
        print("  凶手就在这栋房子里。")
        pause("  （按回车走进山庄）")

        header("人物")
        print("  沈青禾，二十六岁，陆鸿声的外甥女兼秘书。")
        print("  父母早逝，由陆鸿声养大。她今晚穿一件深红色羊毛开衫。")
        print()
        print("  顾行舟，四十二岁，医生，陆鸿声的老友。")
        print("  他检查了尸体，也是新遗嘱的见证人之一。")
        print()
        print("  罗坤，五十岁，山庄管家。他在山庄干了三十年。")
        print("  是他撞开了书房的门。")
        print()
        print("  许南枝，三十五岁，陆鸿声的生意伙伴。")
        print("  晚餐时，她刚和死者大吵过一架。")
        pause("  （按回车继续）")

        header("规则")
        print("  输入数字选择，回车确认。")
        print("  在调查菜单里输入 a 指认，n 查看笔记，h 获取提示，q 退出。")
        print("  在子菜单里，0 是返回。")
        print()
        print("  不必看遍每一个角落。你觉得够了，就随时输入 a 指认。")
        print("  警察天亮才到。你有的是时间，但没有第二次机会。")
        pause("  （按回车开始调查）")

    # ------------------------------------------------------------------
    # 主循环
    # ------------------------------------------------------------------
    def run(self):
        self.intro()
        while not self.finished:
            self.hub()
        print()
        print("  感谢游玩《雨夜留声》。")

    def hub(self):
        header("听雨山庄 · 深夜 21:55")
        print("  雨点敲着窗。客厅里的钟走得很慢。")
        print("  天亮之前，你还有时间。")
        print()
        print("  调查：")
        print(f"   1. 二楼书房（案发现场）{self.mark('loc_study')}")
        print(f"   2. 一楼客厅{self.mark('loc_living')}")
        print(f"   3. 沈青禾的房间{self.mark('loc_shen_room')}")
        print(f"   4. 地下室与后楼梯{self.mark('loc_basement')}")
        print()
        print("  交谈：")
        print(f"   5. 沈青禾{self.mark('talk_shen')}")
        print(f"   6. 顾行舟{self.mark('talk_gu')}")
        print(f"   7. 罗坤{self.mark('talk_luo')}")
        print(f"   8. 许南枝{self.mark('talk_xu')}")
        print()
        print("   0/n 笔记    a 指认    h 提示    q 退出")
        print("   带 * 的地方，你已经去过。")
        print()

        choice = self.ask("  选择：", {"0", "1", "2", "3", "4", "5", "6", "7", "8", "a"})
        if choice == "0":
            self.notebook()
        elif choice == "a":
            self.accuse()
        elif choice == "1":
            self.study()
        elif choice == "2":
            self.living_room()
        elif choice == "3":
            self.shen_room()
        elif choice == "4":
            self.basement()
        elif choice == "5":
            self.talk_shen()
        elif choice == "6":
            self.talk_gu()
        elif choice == "7":
            self.talk_luo()
        elif choice == "8":
            self.talk_xu()

    # ------------------------------------------------------------------
    # 地点：书房
    # ------------------------------------------------------------------
    def study(self):
        self.seen.add("loc_study")
        while True:
            header("二楼书房")
            print("  壁炉里的火还在响。陆鸿声的尸体停在书桌和壁炉之间，")
            print("  像一句没写完的句子。空气里有一股淡淡的火药味。")
            print()
            print("   1. 检查尸体")
            print("   2. 检查书桌")
            print("   3. 检查留声机")
            print("   4. 检查壁炉")
            print("   5. 检查门窗")
            print("   0. 返回客厅")
            choice = self.ask("  选择：", {"0", "1", "2", "3", "4", "5"})
            if choice == "0":
                return
            elif choice == "1":
                self.study_body()
            elif choice == "2":
                self.study_desk()
            elif choice == "3":
                self.study_gramophone()
            elif choice == "4":
                self.study_fire()
            elif choice == "5":
                self.study_door()

    def study_body(self):
        if not self.first("study_body"):
            print("  你又看了一遍尸体。腕表仍停在 21:05。")
            pause()
            return
        print("  陆鸿声仰面倒在壁炉前，深灰色的睡袍被血浸透。")
        print("  左胸的枪伤周围没有火药灼痕。顾行舟说过，")
        print("  这意味着枪口离他至少有一英尺——不是贴着皮肤开的枪。")
        print()
        print("  他的左手腕上有一块银壳腕表。表蒙碎了，指针停在 21:05。")
        print("  表蒙的裂纹向里凹，手腕下面有一块淤青，")
        print("  像是摔倒时撞在桌脚上。")
        print()
        print("  右手边扔着一把左轮手枪。枪是陆鸿声自己的，")
        print("  原本锁在书桌抽屉里。")
        self.add_clue(
            "watch",
            "死者腕表停在 21:05，表蒙向内碎裂，手腕有淤青。",
            "时间",
        )
        self.add_clue(
            "gunshot",
            "左胸枪伤周围没有火药灼痕，枪口距离较远，不是自杀。",
            "现场",
        )
        pause()

    def study_desk(self):
        if not self.first("study_desk"):
            print("  书桌上的遗嘱、账本和复写纸还在原处。")
            pause()
            return
        print("  书桌上摊着一份新遗嘱，墨迹已经干了。")
        print("  日期是今天下午，见证人是顾行舟和罗坤。")
        print("  遗嘱把听雨山庄和大部分收藏捐给“鸿声剧团基金会”；")
        print("  沈青禾只得到一笔按月支付的生活费。")
        print()
        print("  书桌抽屉被拉开了，没有撬痕。里面原本放枪套，现在空了。")
        print("  枪套下面压着一本账本。账本里夹着一张银行催款单：")
        print("  三千元，签名是“沈青禾”。签名旁边有一行红笔字，")
        print("  是陆鸿声的笔迹：“伪造。明早问她。”")
        print()
        print("  打字机旁有一张复写纸，上面是遗嘱的最后一页。")
        print("  沈青禾负责陆鸿声所有的文书。")
        self.add_clue(
            "will",
            "今天下午的新遗嘱把山庄捐给基金会，沈只得到生活费；遗嘱由沈打字。",
            "动机",
        )
        self.add_clue(
            "forgery",
            "账本里有沈青禾伪造的三千元签名，陆批注：明早问她。",
            "动机",
        )
        self.add_clue(
            "gun_drawer",
            "书桌抽屉没有撬痕，枪套空了；凶手知道枪放在哪里。",
            "现场",
        )
        pause()

    def study_gramophone(self):
        if not self.first("study_gramophone"):
            print("  留声机的唱盘还在转，唱针停在收尾槽里。")
            pause()
            return
        print("  一台落地式留声机立在窗边，喇叭正对着门口。")
        print("  唱盘还在转，唱针停在最外圈的收尾槽里，发出沙沙的干响。")
        print()
        print("  唱片是一张十二英寸的试音盘，标签上印着：")
        print("  “《雷雨》音效集 · 第三面：风雨 / 雷声 / 枪声”")
        print("  这是鸿声剧团当年做的非卖品，市面上买不到。")
        print()
        print("  唱片套不见了。音量旋钮被拧到最大。")
        print("  摇柄上挂着一根深红色羊毛纤维。")
        self.add_clue(
            "record",
            "留声机里是《雷雨》音效盘，最后一段是枪声；唱针停在收尾槽。",
            "现场",
        )
        self.add_clue(
            "fiber",
            "留声机摇柄上有一根深红色羊毛纤维。",
            "现场",
        )
        if self.has("cardigan"):
            if self.add_clue(
                "fiber_match",
                "摇柄上的纤维与沈青禾开衫袖口的断口吻合。",
                "现场",
            ):
                print("  你想起沈青禾开衫袖口的断口。颜色、粗细都一样。")
        pause()

    def study_fire(self):
        if not self.first("study_fire"):
            print("  壁炉里的火还在烧，房间里依旧闷热。")
            pause()
            return
        print("  壁炉里的火烧得极旺，松木噼啪作响。")
        print("  房间里闷热得反常，你的后背已经出了一层汗。")
        print("  炉膛里塞着三根还没烧透的松木，像是有人一次添进去的。")
        print("  墙上的温度计指着 28°C。")
        self.add_clue(
            "fire",
            "书房壁炉被添了三大根松木，室温 28°C，尸冷会变慢。",
            "时间",
        )
        pause()

    def study_door(self):
        if not self.first("study_door"):
            print("  门是弹簧锁，窗户从里面闩着。")
            pause()
            return
        print("  门是旧式的弹簧锁，从外面带上就会锁，不用钥匙。")
        print("  门框和锁舌都没有撬痕。钥匙还插在里面的锁孔里——")
        print("  但在这扇门上，钥匙只是用来反锁的，平时根本用不着。")
        print()
        print("  窗户从里面闩着，窗台干燥。")
        print("  窗外是湿滑的陡坡，雨声里夹着碎石滚落的声音。")
        self.add_clue(
            "door",
            "书房门是弹簧锁，带上就锁；窗户从里面闩着。",
            "现场",
        )
        pause()

    # ------------------------------------------------------------------
    # 地点：客厅
    # ------------------------------------------------------------------
    def living_room(self):
        self.seen.add("loc_living")
        while True:
            header("一楼客厅")
            print("  客厅正上方就是书房。牌桌上摊着没打完的牌，")
            print("  壁炉里的火已经暗了。你、沈青禾、罗坤刚才就坐在这里。")
            print()
            print("   1. 回想枪响前的声音")
            print("   2. 检查牌桌与壁钟")
            print("   3. 看看通往楼上的路")
            print("   0. 返回")
            choice = self.ask("  选择：", {"0", "1", "2", "3"})
            if choice == "0":
                return
            elif choice == "1":
                self.living_recall()
            elif choice == "2":
                self.living_table()
            elif choice == "3":
                self.living_route()

    def living_recall(self):
        if not self.first("living_recall"):
            print("  你再次闭上眼睛。楼上的沙沙声，枪响前的寂静。")
            pause()
            return
        print("  你闭上眼睛，把那一刻重新过了一遍。")
        print()
        print("  九点三十五左右，沈青禾说去拿披肩。")
        print("  她走后，楼上似乎一直有一种沙沙的、像雨又不像雨的声音，")
        print("  从天花板的方向传下来。你当时以为那是风穿过瓦缝。")
        print()
        print("  九点四十，枪响了。声音很闷，像隔着一层门板。")
        self.add_clue(
            "muffled",
            "21:40 枪声很闷；枪响前楼上有持续的沙沙声。",
            "时间",
        )
        pause()

    def living_table(self):
        if not self.first("living_table"):
            print("  牌桌上还摊着那副没打完的牌。")
            pause()
            return
        print("  牌桌上散着扑克牌。沈青禾的位置前放着一副没发完的牌。")
        print("  壁钟是机械的，停电后也没停。指针指着九点五十六。")
        print("  你想起枪响的时候，她刚坐下，手里还捏着那张没发出去的牌。")
        print()
        print("  她回来时有些喘，说楼梯太暗，走快了。")
        pause()

    def living_route(self):
        if not self.first("living_route"):
            print("  主楼梯的灯坏了。厨房后面还有一道后楼梯。")
            pause()
            return
        print("  客厅正对着主楼梯。从楼梯上去，往左是书房，往右是东厢。")
        print("  主楼梯的灯坏了，只有楼下一盏煤油灯照着。")
        print()
        print("  你想起厨房后面还有一道后楼梯，也能上二楼，")
        print("  而且不用经过客厅。")
        self.add_clue(
            "backstairs",
            "厨房后门有一道后楼梯，能绕开客厅上二楼，通往书房走廊。",
            "现场",
        )
        pause()

    # ------------------------------------------------------------------
    # 地点：沈青禾的房间
    # ------------------------------------------------------------------
    def shen_room(self):
        self.seen.add("loc_shen_room")
        while True:
            header("沈青禾的房间")
            print("  东厢很小，收拾得过分整齐。")
            print("  床头放着一本《雷雨》的剧本，书页间夹着一张旧剧照。")
            print("  窗外是雨。屋里有一盏煤油灯，灯芯剪得很短。")
            print()
            print("   1. 书桌与唱片目录")
            print("   2. 衣柜")
            print("   3. 床头与皮箱")
            print("   0. 返回")
            choice = self.ask("  选择：", {"0", "1", "2", "3"})
            if choice == "0":
                return
            elif choice == "1":
                self.shen_desk()
            elif choice == "2":
                self.shen_wardrobe()
            elif choice == "3":
                self.shen_bedside()

    def shen_desk(self):
        if not self.first("shen_desk"):
            print("  唱片目录、当票和催债信还摊在桌上。")
            pause()
            return
        print("  桌上摊着一本厚厚的唱片目录。")
        print("  每一张唱片都有编号、来源和存放位置。")
        print("  最后一条写着：")
        print("  “《雷雨》音效集，第三面，借出试听（沈），未还。”")
        print("  日期是两天前。")
        print()
        print("  目录下面压着一张当票：当品是陆鸿声珍藏的《空城计》唱片，")
        print("  当金二百元。旁边还有几封催债信，落款“永利号”。")
        print("  最后一封写着：“月底再不还三千，就把你的事告诉你舅舅。”")
        self.add_clue(
            "catalog",
            "沈青禾的目录写着《雷雨》音效盘第三面借出试听，未还。",
            "人物",
        )
        self.add_clue(
            "debt",
            "沈青禾当掉了陆的唱片，欠“永利号”三千元，被威胁告诉舅舅。",
            "动机",
        )
        pause()

    def shen_wardrobe(self):
        if not self.first("shen_wardrobe"):
            print("  衣柜里那件深红色开衫还挂着，袖口少了一小截。")
            pause()
            return
        print("  衣柜里挂着几件素色衣服。最外面是一件深红色羊毛开衫，")
        print("  袖口有一处新的勾线，少了一小截。")
        print("  断口很齐，像是被什么金属钩住后扯断的。")
        print()
        print("  衣柜底层有一双布鞋，鞋面是湿的，鞋底沾着湿灰。")
        self.add_clue(
            "cardigan",
            "沈青禾的深红色开衫袖口少了一截，断口很新。",
            "人物",
        )
        if self.has("fiber"):
            if self.add_clue(
                "fiber_match",
                "开衫袖口的断口与留声机摇柄上的纤维吻合。",
                "现场",
            ):
                print("  你想起留声机摇柄上的那根深红色纤维。")
        pause()

    def shen_bedside(self):
        if not self.first("shen_bedside"):
            print("  剧本、剧照和那只收拾好的皮箱还在原处。")
            pause()
            return
        print("  《雷雨》的剧本翻到第四幕。夹在里面的剧照上，")
        print("  年轻的陆鸿声穿着长衫站在舞台中央，")
        print("  旁边是一个眉眼像沈青禾的女人。")
        print("  照片背面写着一行褪色的字：“民国十七年，鸿声剧团。”")
        print()
        print("  剧本的扉页上，有人用铅笔写了一行小字：")
        print("  “舅舅说，等这场雨停了，就送我去车站。”")
        print()
        print("  床底下有一只小皮箱，已经收拾好了。")
        print("  最上面放着一张去上海的车票，日期是明天。")
        self.add_clue(
            "suitcase",
            "沈青禾的床下有一只收拾好的皮箱和明天去上海的车票。",
            "人物",
        )
        pause()

    # ------------------------------------------------------------------
    # 地点：地下室与后楼梯
    # ------------------------------------------------------------------
    def basement(self):
        self.seen.add("loc_basement")
        while True:
            header("地下室与后楼梯")
            print("  地下室潮湿，发电机在角落里轰鸣。")
            print("  煤油灯照出一排排旧木箱，空气里有酒味和机油味。")
            print("  后楼梯从厨房后面通上来，木阶很陡，扶手上积着一层薄灰。")
            print()
            print("   1. 后楼梯")
            print("   2. 酒窖")
            print("   3. 罗坤的工具间")
            print("   0. 返回")
            choice = self.ask("  选择：", {"0", "1", "2", "3"})
            if choice == "0":
                return
            elif choice == "1":
                self.basement_stairs()
            elif choice == "2":
                self.basement_wine()
            elif choice == "3":
                self.basement_tools()

    def basement_stairs(self):
        if not self.first("basement_stairs"):
            print("  后楼梯的湿鞋印还在。")
            pause()
            return
        print("  木阶很陡，扶手上的灰被蹭掉了一道，")
        print("  像是有人最近匆匆走过。")
        print("  从后楼梯上去，左边是书房，右边是东厢。")
        print("  楼梯口有一扇小窗，雨丝从窗缝里飘进来，")
        print("  把最上面两级台阶打湿了。湿灰上有一枚不大的鞋印。")
        self.add_clue(
            "backstairs",
            "后楼梯能绕开客厅上二楼，左边书房、右边东厢；台阶上有新鞋印。",
            "现场",
        )
        pause()

    def basement_wine(self):
        if not self.first("basement_wine"):
            print("  酒窖里那只喝了一半的白兰地还在。")
            pause()
            return
        print("  酒窖的门虚掩着。架子上的酒少了几瓶，")
        print("  角落里藏着一只喝了一半的白兰地。")
        print("  瓶口没有灰尘，是今晚开的。")
        self.add_clue(
            "wine",
            "罗坤今晚在酒窖喝过酒；他说不清 21:05 的行踪。",
            "人物",
        )
        pause()

    def basement_tools(self):
        if not self.first("basement_tools"):
            print("  工具间里，那把湿伞还靠在墙边。")
            pause()
            return
        print("  工具间的墙上挂着一把油纸伞，伞面还在滴水。")
        print("  桌上摊着一张山庄出售合同的草稿，买方是许南枝的公司。")
        print("  合同最后一页有一行铅笔字：“新主人留用罗坤。”")
        print("  旁边是罗坤的笔迹：“留不留，谁知道。”")
        self.add_clue(
            "sale",
            "陆鸿声要把山庄卖给许南枝的公司，罗坤可能被解雇。",
            "动机",
        )
        pause()

    # ------------------------------------------------------------------
    # 交谈
    # ------------------------------------------------------------------
    def interview(self, name, intro, topics, handler):
        header(f"与{name}交谈")
        print(intro)
        while True:
            print()
            print("  你想问：")
            for i, (key, label) in enumerate(topics, 1):
                mark = "  *" if f"ask_{name}_{key}" in self.seen else ""
                print(f"   {i}. {label}{mark}")
            print("   0. 结束谈话")
            valid = {str(i) for i in range(1, len(topics) + 1)} | {"0"}
            choice = self.ask("  选择：", valid)
            if choice == "0":
                return

            key, _label = topics[int(choice) - 1]
            mark_key = f"ask_{name}_{key}"
            if mark_key in self.seen:
                print("  这个问题你已经问过了。")
                pause()
                continue
            self.seen.add(mark_key)
            handler(key)
            pause()

    # -------------------------- 沈青禾 --------------------------
    def talk_shen(self):
        self.seen.add("talk_shen")
        topics = [
            ("alibi", "今晚的行踪"),
            ("will", "新遗嘱"),
            ("records", "唱片"),
            ("debt", "三千元"),
        ]
        if self.has("fiber_match"):
            topics.append(("fiber", "这根纤维，你怎么解释？"))
        if self.has("record", "muffled"):
            topics.append(("sound", "枪响之前，楼上有什么声音？"))

        intro = (
            "  沈青禾坐在床沿，双手交叠放在膝上。\n"
            "  她已经换下了那件深红色开衫，穿着一件素色旗袍。\n"
            "  她很安静，眼睛有些红，但说话条理清楚。"
        )
        self.interview("沈青禾", intro, topics, self.shen_topic)

    def shen_topic(self, key):
        if key == "alibi":
            print("  “吃完晚饭，舅舅说想一个人待着。我回房间整理唱片目录，")
            print("  一直到九点三十五。然后我去客厅，跟你们打牌。”")
            print("  她顿了一下。")
            print("  “枪响的时候，我就在你对面。你看见的。”")
            self.add_clue(
                "shen_alibi",
                "沈青禾说 21:00–21:35 独自在房间，21:35 到客厅，21:40 在牌桌旁。",
                "人物",
            )
        elif key == "will":
            print("  “舅舅下午改了遗嘱。我是他的秘书，当然知道。”")
            print("  她看着自己的手。")
            print("  “他把山庄捐给基金会，只给我每月的生活费。")
            print("  他说我不争气。也许他说得对。”")
        elif key == "records":
            print("  “舅舅的唱片都是我整理的。剧团的老录音、音效盘，")
            print("  还有一些孤本。最近我在给它们编目。”")
            print("  她抬起眼睛。")
            print("  “怎么了？唱片有什么问题吗？”")
            self.add_clue(
                "shen_records",
                "沈青禾负责整理陆鸿声的全部唱片，熟悉每一张的内容。",
                "人物",
            )
        elif key == "debt":
            print("  她的肩膀绷紧了。")
            print("  “……你连这个也知道了。”")
            print("  “是，我挪用了三千块。我欠了债。")
            print("  舅舅说，明天早上让我自己说清楚。”")
            print("  她咬了咬嘴唇。")
            print("  “他没说要报警。他只是……很失望。”")
        elif key == "fiber":
            print("  你把那根深红色羊毛纤维放在她面前。")
            print("  她看了很久，没有伸手去碰。")
            print("  “我下午给唱片除尘的时候，可能蹭到了。”")
            print("  “程先生，一根线说明不了什么。你在找一个人，")
            print("  可你找错了。”")
            print("  她的声音很稳，但手指在膝盖上收紧了。")
            self.add_clue(
                "shen_denial",
                "面对纤维，沈青禾说是下午给唱片除尘时蹭到的。",
                "人物",
            )
        elif key == "sound":
            print("  “九点四十的枪声很闷。”你说，")
            print("  “而且枪响之前，楼上有一种沙沙的声音。”")
            print("  沈青禾抬起头。她的眼神第一次有些散。")
            print("  “雨声吧。”")
            print("  “雨声不会从天花板里传下来。”")
            print("  她沉默了很久，然后轻轻说：")
            print("  “程先生，你到底想说什么？”")
            self.add_clue(
                "shen_nervous",
                "提到枪声前的沙沙声时，沈青禾第一次露出慌乱。",
                "人物",
            )

    # -------------------------- 顾行舟 --------------------------
    def talk_gu(self):
        self.seen.add("talk_gu")
        topics = [
            ("time", "死亡时间"),
            ("wound", "枪伤"),
            ("shot", "九点四十的枪声"),
            ("old", "旧事与许南枝"),
        ]
        if self.has("watch"):
            topics.append(("watch", "这块表停在九点零五"))
        if self.has("will"):
            topics.append(("letter", "陆鸿声留下过什么话？"))

        intro = (
            "  顾行舟在书房外面的走廊里抽烟。\n"
            "  他的医生箱放在脚边，箱扣没有扣好。\n"
            "  他看起来很疲惫，但手很稳。"
        )
        self.interview("顾行舟", intro, topics, self.gu_topic)

    def gu_topic(self, key):
        if key == "time":
            print("  “尸温、尸僵，加上肝温，我初步判断在九点二十到九点五十之间。”")
            print("  他吐出一口烟。")
            print("  “但书房太热了。壁炉一直烧着，室温二十八度，")
            print("  尸体会冷得慢。实际死亡时间可能更早。")
            print("  如果火是九点以后才烧旺的，误差可能有半小时。”")
            self.add_clue(
                "gu_time",
                "顾行舟判断死亡时间在 21:20–21:50；高温会让尸冷变慢，实际可能更早。",
                "时间",
            )
        elif key == "wound":
            print("  “左胸，近距离，但不是接触射击。")
            print("  伤口周围没有火药灼痕，枪口至少离他一英尺。”")
            print("  他把烟按灭。")
            print("  “自杀的人不会把枪拿那么远。这是他杀。”")
            if "gunshot" not in self.clues:
                self.add_clue(
                    "gunshot",
                    "顾行舟确认枪口距离较远，不是自杀。",
                    "现场",
                )
        elif key == "shot":
            print("  “很闷。像隔着一层门板，或者隔着一层厚布。”")
            print("  “我当时在图书馆，收音机开着。")
            print("  枪响之前，我什么也没听见。枪响之后，我才把收音机关掉。”")
            self.add_clue(
                "radio",
                "顾行舟和许南枝在图书馆，收音机一直开着，盖住了 21:05 的枪声。",
                "时间",
            )
        elif key == "old":
            print("  他的脸色沉了下来。")
            print("  “十年前，一台手术。出了事，他是唯一知道内情的人。”")
            print("  “他拿这件事捏了我十年。我今晚来，是想跟他做个了断。")
            print("  不是那种了断。”")
            print("  他看了你一眼。")
            print("  “你可以怀疑我。但死亡时间不会替你撒谎。”")
            self.add_clue(
                "gu_motive",
                "陆鸿声曾用十年前的医疗事故要挟顾行舟。",
                "动机",
            )
            print()
            print("  “至于许南枝……我们今晚一直在图书馆。")
            print("  你不必用那种眼神看我。是，我和她在一起。")
            print("  所以她的证词和我的证词，你都可以不信。")
            print("  但我们确实没有离开过。”")
        elif key == "watch":
            print("  “我检查过了。表蒙是从外向里碎的，")
            print("  他的左手腕有一块对应的淤青。摔下去的时候磕在桌脚上。”")
            print("  “表停在九点零五。表不会说谎，但尸体所处的环境会。”")
            print("  他看了你一眼。")
            print("  “如果你能证明火是什么时候烧旺的，")
            print("  你就能证明他是什么时候死的。”")
        elif key == "letter":
            print("  “他今天下午跟我说，他给沈青禾留了一条后路。”")
            print("  “只要她明早肯认错，他就不报警。他连车票都给她买好了。”")
            print("  顾行舟看着窗外的雨。")
            print("  “他这个人，一辈子强硬，到最后还是心软。”")
            self.add_clue(
                "letter",
                "顾行舟说陆鸿声给沈青禾留了后路：认错就不报警，还买了车票。",
                "动机",
            )

    # -------------------------- 罗坤 --------------------------
    def talk_luo(self):
        self.seen.add("talk_luo")
        topics = [
            ("alibi", "今晚的行踪"),
            ("thud", "九点零五的闷响"),
            ("door", "书房的门"),
            ("sale", "山庄、唱片和后楼梯"),
            ("after", "九点三十五，沈青禾离开过吗？"),
            ("umbrella", "你的伞怎么是湿的？"),
        ]

        intro = (
            "  罗坤站在厨房门口，手里攥着一顶旧帽子。\n"
            "  他的靴子上沾着泥，身上有酒气。他不敢看你的眼睛。"
        )
        self.interview("罗坤", intro, topics, self.luo_topic)

    def luo_topic(self, key):
        if key == "alibi":
            print("  “停电以后我就去了地下室。发电机老毛病，")
            print("  我弄了一个多钟头。”")
            print("  “九点半左右上来，跟你们打牌。后来枪响，")
            print("  我就跟你们一起上楼。”")
            self.add_clue(
                "luo_alibi",
                "罗坤说 21:00–21:30 在地下室修发电机，21:30 到客厅。",
                "人物",
            )
        elif key == "thud":
            print("  他的喉结动了一下。")
            print("  “……你怎么知道？”")
            print("  “我是听见一声闷响，像什么东西倒了。")
            print("  我以为是雷，或者后山的落石。”")
            print("  他低下头。")
            print("  “我当时在酒窖里……喝了两口。你别告诉别人。”")
            self.add_clue(
                "thud",
                "罗坤在 21:05 左右听到一声闷响，以为是雷；他当时在酒窖喝酒。",
                "时间",
            )
        elif key == "door":
            print("  “那门是弹簧锁，带上就锁，不用钥匙。")
            print("  钥匙插在里头，外面就打不开。”")
            print("  “你们上来的时候，门是从里面锁着的，我只能撞开。”")
            if "door" not in self.clues:
                self.add_clue(
                    "door",
                    "书房门是弹簧锁，带上就锁；罗坤撞开门时，门确实锁着。",
                    "现场",
                )
        elif key == "sale":
            print("  “陆先生要把山庄卖给许小姐的公司。")
            print("  我在这里干了三十年，他说新主人会留我。”")
            print("  他苦笑了一下。")
            print("  “留不留，谁知道呢。”")
            print()
            print("  “阁楼上有几箱旧唱片，都是剧团的。沈小姐最近在整理。")
            print("  我不懂那些。”")
            print("  他想了想。")
            print("  “不过她倒是常往上跑。那些纸袋子，她比自己的衣服还熟。”")
            print()
            print("  “后楼梯？从厨房后面的小门进去，能直接上二楼，")
            print("  不用经过客厅。左边是书房，右边是东厢。")
            print("  沈小姐常走那条路。她说大楼梯的灯坏了，怕黑。”")
            if "backstairs" not in self.clues:
                self.add_clue(
                    "backstairs",
                    "后楼梯能绕开客厅上二楼；沈青禾常走这条路。",
                    "现场",
                )
        elif key == "after":
            print("  “离开过。她说去拿披肩，走了大概四五分钟。”")
            print("  “我那时候在洗牌，没太注意。")
            print("  她回来的时候有点喘，说楼梯太暗。”")
        elif key == "umbrella":
            print("  “我去看了看发电机棚，还有后山的排水沟。")
            print("  雨这么大，不看一眼不放心。”")
            print("  他顿了顿。")
            print("  “我没上山，也没过桥。你别多想。”")

    # -------------------------- 许南枝 --------------------------
    def talk_xu(self):
        self.seen.add("talk_xu")
        topics = [
            ("quarrel", "晚餐时的争吵"),
            ("alibi", "九点四十，你在哪里？"),
            ("shen", "沈青禾"),
            ("gramophone", "留声机与山庄"),
        ]

        intro = (
            "  许南枝坐在图书馆的扶手椅里，手里夹着一支没点的烟。\n"
            "  她面前的茶几上放着一只空茶杯。\n"
            "  她看着你，像在看一个迟到的人。"
        )
        self.interview("许南枝", intro, topics, self.xu_topic)

    def xu_topic(self, key):
        if key == "quarrel":
            print("  “我父亲的公司被他吞了。我来要个说法。”")
            print("  “他说：‘明天你就知道谁说了算。’”")
            print("  她把烟折断。")
            print("  “我恨不得杀了他。但我没动手。你爱信不信。”")
            self.add_clue(
                "xu_motive",
                "许南枝的父亲公司被陆鸿声吞并，晚餐时她威胁过他。",
                "动机",
            )
        elif key == "alibi":
            print("  “我和顾行舟在图书馆。收音机开着，放的是《毛毛雨》。”")
            print("  “枪响的时候，我们刚关掉收音机。然后一起上楼。”")
            self.add_clue(
                "xu_alibi",
                "许南枝说 21:00–21:50 与顾行舟在图书馆，收音机开着。",
                "人物",
            )
            print()
            print("  “是，我们在一起。”")
            print("  她把断掉的烟扔进烟灰缸。")
            print("  “所以他的证词和我的证词，你都可以不信。")
            print("  但我们确实没离开过图书馆。”")
            self.add_clue(
                "affair",
                "许南枝承认与顾行舟有私情，两人的不在场证明互相依赖。",
                "人物",
            )
        elif key == "shen":
            print("  “那个姑娘？她一直很安静。晚餐时她一句话都没说。")
            print("  陆鸿声骂她的时候，她连头都没抬。”")
            print("  她想了想。")
            print("  “不过，九点三十五左右，我去厨房倒水，")
            print("  看见她从后楼梯上去。走得很急，没看见我。”")
            print("  “她上楼以后，往书房那边拐了。")
            print("  我当时以为她去找陆鸿声。”")
            self.add_clue(
                "xu_saw",
                "许南枝在 21:35 看见沈青禾从后楼梯上楼，往书房方向走。",
                "人物",
            )
        elif key == "gramophone":
            print("  “陆鸿声的留声机？我没碰过。")
            print("  那玩意儿一放，整栋房子都听得见。”")
            print("  她看了你一眼。")
            print("  “你问这个干什么？难道九点四十那声枪响，")
            print("  是留声机放出来的？”")
            print()
            print("  “我本来要买下这里，开一家疗养院。现在？”")
            print("  她看着窗外的雨。")
            print("  “出了人命，谁还买。”")

    # ------------------------------------------------------------------
    # 指认
    # ------------------------------------------------------------------
    def accuse(self):
        header("指认")
        print("  你合上笔记本。客厅里的人都看着你。")
        print("  “我知道是谁杀了陆鸿声。”")
        print()
        print("  第一个问题：凶手是谁？")
        print("   1. 沈青禾")
        print("   2. 顾行舟")
        print("   3. 罗坤")
        print("   4. 许南枝")
        print("   0. 再想想")
        choice = self.ask("  选择：", {"0", "1", "2", "3", "4"})
        if choice == "0":
            print("  你决定再想想。")
            pause()
            return

        culprit = {"1": "shen", "2": "gu", "3": "luo", "4": "xu"}[choice]
        if culprit != "shen":
            names = {"gu": "顾行舟", "luo": "罗坤", "xu": "许南枝"}
            feedback = {
                "gu": (
                    "顾行舟有动机，也有医学知识。但他是第一个指出枪伤不是自杀的人；\n"
                    "  如果他是凶手，他不会拆穿自己布置的“自杀”。\n"
                    "  更重要的是，21:40 枪响时，他在图书馆。那声枪响本身才是关键。"
                ),
                "luo": (
                    "罗坤熟悉这栋房子，也有动机。但他不知道留声机上那张唱片，\n"
                    "  而且他主动说出了 21:05 的闷响——一个凶手不会把真正的时间交给别人。"
                ),
                "xu": (
                    "许南枝有动机，但她和顾行舟在图书馆。\n"
                    "  除非你认定他们合谋，否则她无法在 21:35 启动书房的留声机。"
                ),
            }
            print()
            print(f"  你指认了{names[culprit]}。")
            print(f"  {feedback[culprit]}")
            self.wrong += 1
            pause()
            return

        # 凶手答对了，继续问手法。
        print()
        print("  第二个问题：21:40 的枪声，是怎么回事？")
        print("   1. 留声机播放了一张灌有枪声的唱片")
        print("   2. 凶手从窗外开了一枪")
        print("   3. 顾行舟替凶手作了伪证")
        print("   4. 陆鸿声自己走火")
        print("   0. 再想想")
        choice = self.ask("  选择：", {"0", "1", "2", "3", "4"})
        if choice == "0":
            print("  你决定再想想。")
            pause()
            return
        if choice != "1":
            method_feedback = {
                "2": (
                    "窗户从里面闩着，窗台干燥。而且 21:40 枪响时，\n"
                    "  你们都在上楼之前就听到了声音——窗外没有人。"
                ),
                "3": (
                    "顾行舟确实隐瞒了和许南枝的私情，但他没有理由替沈青禾作假。\n"
                    "  枪声是所有人一起听到的，不是他一个人说的。"
                ),
                "4": (
                    "枪口离伤口至少一英尺，不是走火。\n"
                    "  而且 21:40 枪响时，陆鸿声已经死了。"
                ),
            }
            print()
            print("  你指认了沈青禾，但没有解释那声枪响。")
            print(f"  {method_feedback[choice]}")
            self.wrong += 1
            pause()
            return

        # 手法答对了，继续问证据。
        print()
        print("  第三个问题：什么证据能证明陆鸿声真正的死亡时间？")
        print("   1. 停在 21:05 的腕表，和罗坤听到的闷响")
        print("   2. 顾行舟的尸温判断")
        print("   3. 书房门是弹簧锁")
        print("   4. 新遗嘱的签署时间")
        print("   0. 再想想")
        choice = self.ask("  选择：", {"0", "1", "2", "3", "4"})
        if choice == "0":
            print("  你决定再想想。")
            pause()
            return
        if choice != "1":
            evidence_feedback = {
                "2": (
                    "顾行舟自己说过，书房的高温会让尸冷变慢，\n"
                    "  尸温只能给出一个偏晚的范围。它不能证明 21:05。"
                ),
                "3": (
                    "弹簧锁只能解释凶手怎么离开，不能说明死亡时间。"
                ),
                "4": (
                    "遗嘱说明动机，不能说明时间。"
                ),
            }
            print()
            print("  枪声的解释说得通。但你还缺一个能独立指出真实死亡时间的证据。")
            print(f"  {evidence_feedback[choice]}")
            self.wrong += 1
            pause()
            return

        self.reveal()

    # ------------------------------------------------------------------
    # 揭底
    # ------------------------------------------------------------------
    def reveal(self):
        header("真相")
        print("  你没有看沈青禾。你看的是那张唱片。")
        print("  标签上“枪声”两个字，在灯下很清楚。")
        print()
        print("  【21:00】")
        print("  沈青禾从后楼梯上楼。她没有回自己的房间。")
        print("  书房的门虚掩着。陆鸿声坐在壁炉边，")
        print("  桌上摊着下午刚签的遗嘱，旁边是那本账本。")
        print("  她跪下来求他。")
        print("  他没有骂她，只说：“明早，你自己说清楚。说完，你走。”")
        print("  她不信。她看见他眼里的失望，觉得那比愤怒更可怕。")
        print("  她看见了抽屉里的左轮手枪。")
        print()
        print("  【21:05】")
        print("  枪声被雷声吞掉了。")
        print("  陆鸿声倒下时，左手腕撞在桌脚上。")
        print("  表蒙碎了，指针停在九点零五。")
        print("  沈青禾在原地站了很久。然后她开始布置。")
        print("  她忘了那本账本。她满脑子都是时间。")
        print("  她把枪放在他右手边，让现场看起来像自杀。")
        print("  她往壁炉里添了三根松木。火会烧得很旺，房间会变热，")
        print("  尸体会冷得慢——法医给出的死亡时间就会往后推。")
        print("  她从阁楼取来的《雷雨》音效盘已经放在唱盘上，发条上满。")
        print("  她不能现在启动它。她需要它等一会儿再响。")
        pause("  （按回车继续）")

        print()
        print("  【21:30】")
        print("  你下楼时，沈青禾和罗坤已经在牌桌旁。")
        print("  她看起来很平静，只是手指有点凉。")
        print()
        print("  【21:35】")
        print("  她站起来，说去拿披肩。")
        print("  她走后楼梯上楼，进了书房，放下唱针。")
        print("  唱片先放出风雨声。那声音和窗外的雨混在一起，")
        print("  像山谷里的回响。她回到客厅，刚好赶上发牌。")
        print()
        print("  【21:40】")
        print("  唱片里的枪声响了。")
        print("  它隔着门板，传进客厅，听起来闷闷的。")
        print("  你们冲上楼。门是弹簧锁，已经锁上。罗坤撞开门。")
        print("  留声机还在转，唱针停在收尾槽。")
        print("  你们看见尸体、枪、火，看见一个刚刚死去的人。")
        print("  只有那块表，停在九点零五。")
        pause("  （按回车继续）")

        print()
        print("  顾行舟的尸温判断没有错，错的是那间房。")
        print("  火太旺，室温太高，尸体冷得太慢。")
        print("  他给出的时间，比真实死亡时间晚了半个多小时。")
        print()
        print("  罗坤在酒窖里听到的闷响，不是雷。")
        print("  那是九点零五的枪声。")
        print()
        print("  许南枝在九点三十五看见沈青禾从后楼梯上楼，")
        print("  往书房的方向走。沈青禾说她在房间里找披肩，")
        print("  可她的房间在东边，她却往北边去了。")
        print()
        print("  留声机摇柄上的深红色纤维，和她开衫袖口的断口对得上。")
        print("  唱片目录上写着：")
        print("  “《雷雨》音效集，第三面，借出试听（沈），未还。”")
        print()
        print("  你把这些东西一件一件放在桌上。")
        print("  沈青禾看着那张唱片，很久没有说话。")
        pause("  （按回车继续）")

        print()
        print("  “我本来只想让他停下来。”她说。")
        print("  “他说明早让我自己说清楚。我知道那是什么意思。")
        print("  剧团、基金会、报纸……所有人都会知道。”")
        print()
        print("  “他给你买了车票。”你说。")
        print("  “是。”她的眼泪终于掉下来，")
        print("  “他给我买了车票。他说，等我从上海回来，")
        print("  这件事就当没发生过。”")
        print()
        print("  “那你为什么……”")
        print("  “我不信。”她说，“我从来不敢信他。”")
        print()
        print("  天快亮的时候，雨停了。")
        print("  警察从山道上上来，带走了沈青禾。")
        print("  你站在门口，看见她回头看了一眼书房。")
        print("  留声机已经不转了。")
        print("  可那声枪响，还在每个人的耳朵里。")
        pause("  （按回车合上笔记）")

        header("案件回顾")
        print("  凶手：沈青禾")
        print("  真实死亡时间：21:05")
        print("  伪造的枪声：21:40，留声机播放《雷雨》音效盘")
        print("  动机：伪造签名挪用三千元；新遗嘱剥夺继承权；害怕被揭发")
        print("  关键证据：停在 21:05 的腕表、罗坤听到的闷响、")
        print("            留声机里的音效盘、摇柄上的红色纤维、")
        print("            唱片目录上的借出记录、许南枝的目击")
        print()
        print("  红鲱鱼：顾行舟与许南枝的私情、罗坤偷酒、")
        print("          许南枝的威胁、山庄出售、弹簧锁密室。")
        print()
        print(f"  调查记录：{len(self.clues)} 条线索 · {self.hint_index} 次提示 · {self.wrong} 次错误判断")
        if len(self.clues) >= 28:
            print("  你几乎看穿了山庄的每一道缝隙。")
        else:
            print("  你抓住了足够多的细节。")
        print()
        self.finished = True


if __name__ == "__main__":
    try:
        Game().run()
    except SystemExit:
        pass
