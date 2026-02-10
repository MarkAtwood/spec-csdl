# Kangxi 214 Radical Registry

**Version:** 1.0
**Author:** Mark Atwood
**Date:** 2026-02-09
**For:** CJK Stroke Description Language (CSDL) Specification, Appendix B

---

## Purpose

This registry records the standard Kangxi 214 radicals with their
pinyin readings, stroke counts, common positional and simplified
variants, and typical positions in compound characters. It is a
descriptive reference; it does not define CSDL components. Component
definitions (stroke-level build specifications) for each radical are
a separate concern.

Variants use CSDL dotted notation: `base_name.position` or
`base_name.position.qualifier` (e.g., `shui3.left` for 氵,
`jin1.left.simp` for 钅). Variant tags are open-ended lowercase
ASCII identifiers per Section 3 of the CSDL specification; common
tags include `left`, `right`, `top`, `bot`, `inner`, `outer`,
`simp`, `alt`, and compound forms like `left.simp`.

### Disambiguation Notes

**Radicals 74 and 130 (月 moon vs 肉 meat).** These are distinct
radicals that render identically in most modern typefaces when used
as components (both appear as 月). Authors MUST disambiguate using
pinyin: `yue4` for moon-related characters (e.g., 朗, 期), `rou4`
for meat-related characters (e.g., 肝, 脈). This is the author's
responsibility per CSDL Principle 4 (§1.4). CSDL treats
disambiguation as the author's problem; the specification does not
attempt automatic resolution.

**Radicals 163 and 170 (邑 city vs 阜 mound).** Both use the
variant glyph 阝 but in different positions: 邑 appears as 阝 on
the RIGHT (`yi4.right`), while 阜 appears as 阝 on the LEFT
(`fu4.left`). Position is sufficient for disambiguation.

### Pinyin Collision Note

Several radicals share the same pinyin reading. The pinyin values
in this registry are informational labels for human readers. They
do not automatically generate CSDL aliases or component names.

Authors who create pinyin-based aliases for colliding radicals
MUST use distinct names (§10.7). The CSDL variant tag mechanism
provides a natural disambiguation path (e.g., `jin1.axe` for
斤, `jin1.metal` for 金). Per the CSDL specification, each
alias name MUST be unique within a file (§6.9, constraint 25),
and alias names MUST NOT collide with component names (§6.9,
constraint 24).

The complete set of pinyin collisions in this registry:

| Pinyin | Radicals |
|--------|----------|
| bi3 | 21 匕 (spoon), 81 比 (compare) |
| chuan1 | 47 巛 (river) — note: not a true collision if radical 136 舛 uses chuan3 |
| er2 | 10 儿 (legs), 126 而 (and) |
| fang1 | 22 匚 (open box), 70 方 (square) |
| fei1 | 175 非 (wrong), 183 飛 (fly) |
| fu4 | 88 父 (father), 170 阜 (mound) |
| gong1 | 48 工 (work), 57 弓 (bow) |
| gu3 | 150 谷 (valley), 188 骨 (bone), 207 鼓 (drum) |
| ji1 | 16 几 (table) — note: not a true collision if radical 58 彐 uses ji4 |
| jin1 | 50 巾 (towel), 69 斤 (axe), 167 金 (gold) |
| li4 | 19 力 (power), 117 立 (stand), 171 隶 (slave), 193 鬲 (tripod) |
| mao2 | 82 毛 (fur), 110 矛 (spear) |
| mi4 | 14 冖 (cover), 120 糸 (silk) |
| min3 | 108 皿 (dish), 205 黽 (frog) |
| mu4 | 75 木 (tree), 109 目 (eye) |
| shan1 | 46 山 (mountain), 59 彡 (bristle) |
| shi2 | 24 十 (ten), 112 石 (stone), 184 食 (eat) |
| shi3 | 111 矢 (arrow), 152 豕 (pig) |
| shi4 | 33 士 (scholar), 83 氏 (clan), 113 示 (spirit) |
| shou3 | 64 手 (hand), 185 首 (head) |
| shu3 | 202 黍 (millet), 208 鼠 (rat) |
| wu2 | 71 无 (not), 80 毋 (do not) |
| xin1 | 61 心 (heart), 160 辛 (bitter) |
| yi1 | 1 一 (one), 145 衣 (clothes) |
| yi3 | 5 乙 (second) — isolated |
| yi4 | 56 弋 (shoot), 163 邑 (city) |
| yu3 | 124 羽 (feather), 173 雨 (rain) |
| yu4 | 96 玉 (jade), 129 聿 (brush) |
| yue4 | 74 月 (moon), 214 龠 (flute) |
| zhi3 | 34 夂 (go), 77 止 (stop), 204 黹 (embroidery) |
| zhi4 | 133 至 (arrive), 153 豸 (badger) |

---

## Section 1: 1–4 Strokes (Radicals 1–94)

| Rad# | Char | Pinyin | Strokes | Meaning | Variants | Typical Position(s) |
|------|------|--------|---------|---------|----------|---------------------|
| 1 | 一 | yi1 | 1 | one |  | top, bot, component |
| 2 | 丨 | gun3 | 1 | line |  | component |
| 3 | 丶 | zhu3 | 1 | dot |  | component |
| 4 | 丿 | pie3 | 1 | slash |  | component |
| 5 | 乙 | yi3 | 1 | second | 乚 yi3.hook | component |
| 6 | 亅 | jue2 | 1 | hook |  | component |
| 7 | 二 | er4 | 2 | two |  | component |
| 8 | 亠 | tou2 | 2 | lid |  | top |
| 9 | 人 | ren2 | 2 | person | 亻 ren2.left | left, top, component |
| 10 | 儿 | er2 | 2 | legs |  | bot |
| 11 | 入 | ru4 | 2 | enter |  | top, component |
| 12 | 八 | ba1 | 2 | eight |  | top, component |
| 13 | 冂 | jiong1 | 2 | down box |  | outer |
| 14 | 冖 | mi4 | 2 | cover |  | top |
| 15 | 冫 | bing1 | 2 | ice |  | left |
| 16 | 几 | ji1 | 2 | table |  | component |
| 17 | 凵 | kan3 | 2 | open box |  | outer |
| 18 | 刀 | dao1 | 2 | knife | 刂 dao1.right | right, component |
| 19 | 力 | li4 | 2 | power |  | right, component |
| 20 | 勹 | bao1 | 2 | wrap |  | outer |
| 21 | 匕 | bi3 | 2 | spoon |  | right, component |
| 22 | 匚 | fang1 | 2 | open box |  | outer |
| 23 | 匸 | xi4 | 2 | hiding box |  | outer |
| 24 | 十 | shi2 | 2 | ten |  | component |
| 25 | 卜 | bu3 | 2 | divination |  | right, component |
| 26 | 卩 | jie2 | 2 | seal | 㔾 jie2.alt | right |
| 27 | 厂 | han4 | 2 | cliff |  | outer |
| 28 | 厶 | si1 | 2 | private |  | component |
| 29 | 又 | you4 | 2 | again |  | right, component |
| 30 | 口 | kou3 | 3 | mouth |  | left, right, inner, outer, component |
| 31 | 囗 | wei2 | 3 | enclosure |  | outer |
| 32 | 土 | tu3 | 3 | earth | 圡 tu3.alt | left, bot, component |
| 33 | 士 | shi4 | 3 | scholar |  | top, component |
| 34 | 夂 | zhi3 | 3 | go |  | top |
| 35 | 夊 | sui1 | 3 | go slowly |  | bot |
| 36 | 夕 | xi1 | 3 | evening |  | left, component |
| 37 | 大 | da4 | 3 | big |  | top, component |
| 38 | 女 | nv3 | 3 | woman |  | left, component |
| 39 | 子 | zi3 | 3 | child |  | left, component |
| 40 | 宀 | mian2 | 3 | roof |  | top |
| 41 | 寸 | cun4 | 3 | inch |  | right, component |
| 42 | 小 | xiao3 | 3 | small | ⺌ xiao3.top, ⺍ xiao3.top2 | top, component |
| 43 | 尢 | wang1 | 3 | lame | 尣 wang1.alt | component |
| 44 | 尸 | shi1 | 3 | corpse |  | outer |
| 45 | 屮 | che4 | 3 | sprout |  | component |
| 46 | 山 | shan1 | 3 | mountain |  | left, top, bot, component |
| 47 | 巛 | chuan1 | 3 | river | 川 chuan1.alt | left, component |
| 48 | 工 | gong1 | 3 | work |  | left, component |
| 49 | 己 | ji3 | 3 | self | 巳 ji3.alt1, 已 ji3.alt2 | component |
| 50 | 巾 | jin1 | 3 | towel |  | left, bot, component |
| 51 | 干 | gan1 | 3 | dry |  | left, component |
| 52 | 幺 | yao1 | 3 | small, tiny |  | component |
| 53 | 广 | guang3 | 3 | shelter |  | outer |
| 54 | 廴 | yin3 | 3 | long stride |  | outer |
| 55 | 廾 | gong3 | 3 | two hands |  | bot |
| 56 | 弋 | yi4 | 3 | shoot |  | component |
| 57 | 弓 | gong1 | 3 | bow |  | left, component |
| 58 | 彐 | ji4 | 3 | snout | 彑 ji4.alt | top, component |
| 59 | 彡 | shan1 | 3 | bristle |  | right |
| 60 | 彳 | chi4 | 3 | step |  | left |
| 61 | 心 | xin1 | 4 | heart | 忄 xin1.left, ⺗ xin1.bot | left, bot, component |
| 62 | 戈 | ge1 | 4 | halberd |  | right, component |
| 63 | 戶 | hu4 | 4 | door | 户 hu4.simp, 戸 hu4.jp | left, outer |
| 64 | 手 | shou3 | 4 | hand | 扌 shou3.left | left, component |
| 65 | 支 | zhi1 | 4 | branch |  | component |
| 66 | 攴 | pu1 | 4 | strike | 攵 pu1.right | right |
| 67 | 文 | wen2 | 4 | script |  | component |
| 68 | 斗 | dou3 | 4 | dipper |  | right, component |
| 69 | 斤 | jin1 | 4 | axe |  | right, component |
| 70 | 方 | fang1 | 4 | square |  | left, component |
| 71 | 无 | wu2 | 4 | not | 旡 wu2.alt | component |
| 72 | 日 | ri4 | 4 | sun |  | left, top, component |
| 73 | 曰 | yue1 | 4 | say |  | top, component |
| 74 | 月 | yue4 | 4 | moon |  | left, right, component |
| 75 | 木 | mu4 | 4 | tree |  | left, top, bot, component |
| 76 | 欠 | qian4 | 4 | lack |  | right |
| 77 | 止 | zhi3 | 4 | stop |  | left, bot, component |
| 78 | 歹 | dai3 | 4 | death | 歺 dai3.alt | left |
| 79 | 殳 | shu1 | 4 | weapon |  | right |
| 80 | 毋 | wu2 | 4 | do not | 母 wu2.alt | component |
| 81 | 比 | bi3 | 4 | compare |  | left, component |
| 82 | 毛 | mao2 | 4 | fur |  | component |
| 83 | 氏 | shi4 | 4 | clan |  | component |
| 84 | 气 | qi4 | 4 | steam |  | outer |
| 85 | 水 | shui3 | 4 | water | 氵 shui3.left, 氺 shui3.bot | left, bot, component |
| 86 | 火 | huo3 | 4 | fire | 灬 huo3.bot | left, bot, component |
| 87 | 爪 | zhao3 | 4 | claw | 爫 zhao3.top | top, component |
| 88 | 父 | fu4 | 4 | father |  | top, component |
| 89 | 爻 | yao2 | 4 | mix |  | top, component |
| 90 | 爿 | qiang2 | 4 | split wood L |  | left |
| 91 | 片 | pian4 | 4 | split wood R |  | left |
| 92 | 牙 | ya2 | 4 | fang |  | component |
| 93 | 牛 | niu2 | 4 | cow | 牜 niu2.left | left, component |
| 94 | 犬 | quan3 | 4 | dog | 犭 quan3.left | left, component |

## Section 2: 5–6 Strokes (Radicals 95–146)

| Rad# | Char | Pinyin | Strokes | Meaning | Variants | Typical Position(s) |
|------|------|--------|---------|---------|----------|---------------------|
| 95 | 玄 | xuan2 | 5 | dark |  | component |
| 96 | 玉 | yu4 | 5 | jade | 王 yu4.left | left, component |
| 97 | 瓜 | gua1 | 5 | melon |  | component |
| 98 | 瓦 | wa3 | 5 | tile |  | right, component |
| 99 | 甘 | gan1 | 5 | sweet |  | component |
| 100 | 生 | sheng1 | 5 | life |  | component |
| 101 | 用 | yong4 | 5 | use |  | component |
| 102 | 田 | tian2 | 5 | field |  | top, left, component |
| 103 | 疋 | pi3 | 5 | bolt of cloth |  | component |
| 104 | 疒 | ne4 | 5 | illness |  | outer |
| 105 | 癶 | bo4 | 5 | dotted tent |  | top |
| 106 | 白 | bai2 | 5 | white |  | top, left, component |
| 107 | 皮 | pi2 | 5 | skin |  | right, component |
| 108 | 皿 | min3 | 5 | dish |  | bot |
| 109 | 目 | mu4 | 5 | eye |  | left, component |
| 110 | 矛 | mao2 | 5 | spear |  | left, component |
| 111 | 矢 | shi3 | 5 | arrow |  | left, component |
| 112 | 石 | shi2 | 5 | stone |  | left, component |
| 113 | 示 | shi4 | 5 | spirit | 礻 shi4.left | left, bot, component |
| 114 | 禸 | rou2 | 5 | track |  | component |
| 115 | 禾 | he2 | 5 | grain |  | left, top, component |
| 116 | 穴 | xue2 | 5 | cave |  | top |
| 117 | 立 | li4 | 5 | stand |  | left, top, component |
| 118 | 竹 | zhu2 | 6 | bamboo | ⺮ zhu2.top | top |
| 119 | 米 | mi3 | 6 | rice |  | left, top, component |
| 120 | 糸 | mi4 | 6 | silk | 糹 mi4.left, 纟 mi4.left.simp | left, component |
| 121 | 缶 | fou3 | 6 | jar |  | left, component |
| 122 | 网 | wang3 | 6 | net | 罒 wang3.top, ⺲ wang3.top2 | top |
| 123 | 羊 | yang2 | 6 | sheep | ⺶ yang2.top, ⺷ yang2.top2 | top, left, component |
| 124 | 羽 | yu3 | 6 | feather |  | right, component |
| 125 | 老 | lao3 | 6 | old | 耂 lao3.top | top, component |
| 126 | 而 | er2 | 6 | and |  | component |
| 127 | 耒 | lei3 | 6 | plow |  | left |
| 128 | 耳 | er3 | 6 | ear |  | left, component |
| 129 | 聿 | yu4 | 6 | brush | ⺻ yu4.top | top, component |
| 130 | 肉 | rou4 | 6 | meat | ⺼ rou4.left | left, component |
| 131 | 臣 | chen2 | 6 | minister |  | left, component |
| 132 | 自 | zi4 | 6 | self |  | top, component |
| 133 | 至 | zhi4 | 6 | arrive |  | component |
| 134 | 臼 | jiu4 | 6 | mortar |  | top, bot, component |
| 135 | 舌 | she2 | 6 | tongue |  | top, component |
| 136 | 舛 | chuan3 | 6 | oppose |  | component |
| 137 | 舟 | zhou1 | 6 | boat |  | left, component |
| 138 | 艮 | gen4 | 6 | stubborn |  | component |
| 139 | 色 | se4 | 6 | color |  | component |
| 140 | 艸 | cao3 | 6 | grass | 艹 cao3.top | top |
| 141 | 虍 | hu1 | 6 | tiger |  | top |
| 142 | 虫 | chong2 | 6 | insect |  | left, bot, component |
| 143 | 血 | xue4 | 6 | blood |  | component |
| 144 | 行 | xing2 | 6 | walk |  | outer, component |
| 145 | 衣 | yi1 | 6 | clothes | 衤 yi1.left | left, component |
| 146 | 襾 | ya4 | 6 | west cover | 覀 ya4.top | top |

## Section 3: 7–9 Strokes (Radicals 147–189)

| Rad# | Char | Pinyin | Strokes | Meaning | Variants | Typical Position(s) |
|------|------|--------|---------|---------|----------|---------------------|
| 147 | 見 | jian4 | 7 | see | 见 jian4.simp | right, component |
| 148 | 角 | jiao3 | 7 | horn |  | left, component |
| 149 | 言 | yan2 | 7 | speech | 讠 yan2.left.simp | left, component |
| 150 | 谷 | gu3 | 7 | valley |  | component |
| 151 | 豆 | dou4 | 7 | bean |  | component |
| 152 | 豕 | shi3 | 7 | pig |  | component |
| 153 | 豸 | zhi4 | 7 | badger |  | left |
| 154 | 貝 | bei4 | 7 | shell | 贝 bei4.simp | left, bot, component |
| 155 | 赤 | chi4 | 7 | red |  | component |
| 156 | 走 | zou3 | 7 | run |  | outer, component |
| 157 | 足 | zu2 | 7 | foot | ⻊ zu2.left | left, component |
| 158 | 身 | shen1 | 7 | body |  | left, component |
| 159 | 車 | che1 | 7 | cart | 车 che1.simp | left, component |
| 160 | 辛 | xin1 | 7 | bitter |  | component |
| 161 | 辰 | chen2 | 7 | morning |  | component |
| 162 | 辵 | chuo4 | 7 | walk | 辶 chuo4.bot | outer |
| 163 | 邑 | yi4 | 7 | city | 阝 yi4.right | right |
| 164 | 酉 | you3 | 7 | wine |  | left, component |
| 165 | 釆 | bian4 | 7 | distinguish |  | top, component |
| 166 | 里 | li3 | 7 | village |  | component |
| 167 | 金 | jin1 | 8 | gold | 釒 jin1.left, 钅 jin1.left.simp | left, component |
| 168 | 長 | chang2 | 8 | long | 长 chang2.simp | component |
| 169 | 門 | men2 | 8 | gate | 门 men2.simp | outer |
| 170 | 阜 | fu4 | 8 | mound | 阝 fu4.left | left |
| 171 | 隶 | li4 | 8 | slave |  | component |
| 172 | 隹 | zhui1 | 8 | short-tailed bird |  | right, component |
| 173 | 雨 | yu3 | 8 | rain | ⻗ yu3.top | top |
| 174 | 靑 | qing1 | 8 | blue-green | 青 qing1.mod | component |
| 175 | 非 | fei1 | 8 | wrong |  | component |
| 176 | 面 | mian4 | 9 | face |  | component |
| 177 | 革 | ge2 | 9 | leather |  | left, component |
| 178 | 韋 | wei2 | 9 | tanned leather | 韦 wei2.simp | component |
| 179 | 韭 | jiu3 | 9 | leek |  | component |
| 180 | 音 | yin1 | 9 | sound |  | top, component |
| 181 | 頁 | ye4 | 9 | page | 页 ye4.simp | right, component |
| 182 | 風 | feng1 | 9 | wind | 风 feng1.simp | component |
| 183 | 飛 | fei1 | 9 | fly | 飞 fei1.simp | component |
| 184 | 食 | shi2 | 9 | eat | 飠 shi2.left, 饣 shi2.left.simp | left, component |
| 185 | 首 | shou3 | 9 | head |  | top, component |
| 186 | 香 | xiang1 | 9 | fragrant |  | component |
| 187 | 馬 | ma3 | 10 | horse | 马 ma3.simp | left, bot, component |
| 188 | 骨 | gu3 | 10 | bone |  | left, component |
| 189 | 高 | gao1 | 10 | tall |  | top, component |

## Section 4: 10+ Strokes (Radicals 190–214)

| Rad# | Char | Pinyin | Strokes | Meaning | Variants | Typical Position(s) |
|------|------|--------|---------|---------|----------|---------------------|
| 190 | 髟 | biao1 | 10 | hair |  | top |
| 191 | 鬥 | dou4 | 10 | fight |  | outer |
| 192 | 鬯 | chang4 | 10 | herbs |  | component |
| 193 | 鬲 | li4 | 10 | tripod |  | component |
| 194 | 鬼 | gui3 | 10 | ghost |  | component |
| 195 | 魚 | yu2 | 11 | fish | 鱼 yu2.simp | left, component |
| 196 | 鳥 | niao3 | 11 | bird | 鸟 niao3.simp | right, component |
| 197 | 鹵 | lu3 | 11 | salt | 卤 lu3.simp | component |
| 198 | 鹿 | lu4 | 11 | deer |  | component |
| 199 | 麥 | mai4 | 11 | wheat | 麦 mai4.simp | component |
| 200 | 麻 | ma2 | 11 | hemp |  | top, component |
| 201 | 黃 | huang2 | 12 | yellow | 黄 huang2.mod | component |
| 202 | 黍 | shu3 | 12 | millet |  | component |
| 203 | 黑 | hei1 | 12 | black |  | component |
| 204 | 黹 | zhi3 | 12 | embroidery |  | component |
| 205 | 黽 | min3 | 13 | frog | 黾 min3.simp | component |
| 206 | 鼎 | ding3 | 13 | tripod |  | component |
| 207 | 鼓 | gu3 | 13 | drum |  | component |
| 208 | 鼠 | shu3 | 13 | rat |  | component |
| 209 | 鼻 | bi2 | 14 | nose |  | component |
| 210 | 齊 | qi2 | 14 | even | 齐 qi2.simp | component |
| 211 | 齒 | chi3 | 15 | tooth | 齿 chi3.simp | left, component |
| 212 | 龍 | long2 | 16 | dragon | 龙 long2.simp | component |
| 213 | 龜 | gui1 | 16 | turtle | 龟 gui1.simp | component |
| 214 | 龠 | yue4 | 17 | flute |  | component |

---

## Summary Statistics

**Total radicals:** 214

**Total variant forms recorded:** 73

**Radicals by typical position** (a radical may appear in multiple positions):

| Position | Count |
|----------|-------|
| left | 67 |
| right | 24 |
| top | 43 |
| bot | 17 |
| inner | 1 |
| outer | 19 |
| component | 167 |

**Radicals by stroke count:**

| Strokes | Count |
|---------|-------|
| 1 | 6 |
| 2 | 23 |
| 3 | 31 |
| 4 | 34 |
| 5 | 23 |
| 6 | 29 |
| 7 | 20 |
| 8 | 9 |
| 9 | 11 |
| 10 | 8 |
| 11 | 6 |
| 12 | 4 |
| 13 | 4 |
| 14 | 2 |
| 15 | 1 |
| 16 | 2 |
| 17 | 1 |

---

*End of Kangxi 214 Radical Registry*
