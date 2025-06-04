# Nttu CSIE Class: Programming Langue

## 組員
- 陳昱凱
- 林威旭
- 謝尚哲
- 游能順


## 專案內容 : 


### Build an interpreter
本專案使用 Python 和 PLY (Python Lex-Yacc) 來實作一個簡單的直譯器。  


### 語言設計理念

本直譯器的目標是實作一個簡單的 **命令式編程（Imperative Programming）** 語言，並在未來擴展支援其他編程範式，如 **函數式編程（Functional Programming）** 和 **物件導向編程（Object-Oriented Programming）**。以下是主要的設計理念：


## 使用環境
python version:  3.9.6  
tool:
```bash!=
pip install ply
```

## 語言特性

### **1.命令式編程**
  - 語法範例：
  ```txt
   🤕 x = 10
   🤕 y = x * 2
    if y > 15:
        😭("y is large")
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
🤕 x = 😀;
🤕 y = 😫;

if x and not y:
    😭(114514);

```

### for loop
```text
🤕 sum = 0;

for i in range 1 6:
  sum = sum + i;
  
😭(sum);

```

### while loop
```text
🤕 i = 1;
🤕 sum = 0;

😺 i <= 5:
    sum = sum + i;
    i = i + 1;
    😭(sum);
```