# Nttu CSIE Class: Programming Langue

## 組員
- 陳昱凱
- 林威旭
- 謝尚哲
- 游能順


## 專案內容 : 


### Build an interpreter
本專案使用 Python 來實作一個簡單的直譯器。  


### 語言設計理念

本直譯器的目標是實作一個簡單的 **命令式編程（Imperative Programming）** 語言，並在未來擴展支援其他編程範式，如 **函數式編程（Functional Programming）** 和 **物件導向編程（Object-Oriented Programming）**。以下是主要的設計理念：


### 使用環境
python version:  3.9.6  
tool:
```bash!=
pip install ply
```
最後PLY沒用到就是了 ww

## 語法解釋
| 功能            | Emoji            |
|---------------| ---------------- |
| 變數宣告          | 🤕               |
| 加法            | 🤌               |
| 減法            | 😡               |
| 乘法            | ☹️               |
| 除法            | 🤬               |
| 布林真           | 😀               |
| 布林假           | 😫               |
| if            | if               |
| else          | else             |
| while         | 😺               |
| for  in range | 🤐 ... 🤫 🤣 ... |
| break         | 🫥               |
| continue      | 😶               |
| print         | 😭               |
| function      | 🤢               |
| block 結尾      | 🥶               |
| return        | 🍉               |
| switch        | 🤮           |
| case          | 🤧             |
| default       | 😾          |



## 語言特性

### **1.命令式編程**
  - 語法範例：
  ```txt
   🤕 x = 10;
   🤕 y = x * 2;
    if y > 15:
        😭("y is large");
  ```
#### 附值
```text
🤕 a = 10;
🤕 b = "123";
```

### **2.支援基本函數**
- 支援簡單的函數
- 語法範例
```txt
🤢 square(n):
   🍉 n * n;
🥶
😭(square(5));
```

## 使用方式  

### function
```text
🤢 greet:
    😭("bye");
🥶

greet();
```
### if else statement and logic operator
```text
🤕 x 🥳 😀;
🤕 y 🥳 😫;

if x and not y:
    😭(114514);

```

### for loop
```text
🤕 sum 🥳 0;

🤐 i 🤫 🤣  1 6:
  sum 🥳 sum 🤌 i;
🥶
😭(sum);

```
#### break(for)
```text
🤕 sum 🥳 0;

🤐 i 🤫 🤣  1 6:
  sum 🥳 sum 🤌 i;
  🫥;
🥶
😭(sum);
```
#### continue
```text
🤕 sum 🥳 0;

🤐 i 🤫 🤣  1 6:
    😶;
    sum 🥳 sum 🤌 i;
🥶
😭(sum);
```
### while loop
```text
🤕 i 🥳 1;
🤕 sum 🥳 0;

😺 i <= 5:
    sum 🥳 sum 🤌 i;
    i 🥳 i 🤌 1;
🥶
😭(i);
```
#### while break and continue
```text
same as for loop w:w
```
### switch case
```text
🤕 x 🥳 2;
🤮 x:
  🤧 1:
    😭("one");
    🫥;
  🤧 2:
    😭("two");
    🫥;
  🤧 3:
    😭("three");
    🫥;
  😾:
    😭("default");
```
