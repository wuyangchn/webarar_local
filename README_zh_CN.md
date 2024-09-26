
# WebArAr

[English](README.md)

### 目录

1. [介绍](#介绍)
2. [背景](#背景)
3. [使用](#使用)
4. [功能](#功能)
5. [更新记录](#更新记录)
6. [引用 WebArAr 或 ArArPy](#引用-webarar-或-ararpy)
7. [参考资料](#参考资料)

## 介绍

WebArAr是一个基于[Django](https://www.djangoproject.com/) 框架的网络应用程序，用于
<sup>40</sup>Ar/<sup>39</sup>Ar 地质年代学数据处理。

* 后端的主要程序已打包为 [ArArPy](https://github.com/wuyangchn/ararpy.git) ，可通过pip安装，参见 [PyPi](https://pypi.org/project/ararpy/) 。
* Django框架、Bootstrap、Echarts、Bootstrap-table 等提供了直观的交互界面。

访问 [WebArAr](https://www.webarar.net)

## 背景

本项目源于更新和增强现有的 <sup>40</sup>Ar/<sup>39</sup>Ar 测年数据处理工具的需要。
总的来说，ArArCALC 和 Isoplot/IsoplotR 已在该领域得到广泛应用。
然而，有几个因素使得这些工具显现出不足：
(1) ArArCALC 和 Isoplot 是为 Microsoft Excel 早期版本（如 Excel 2003）开发的宏工具，现已缺乏更新，
Isoplot 已不再维护；
(2) 数据处理软件需要新的功能，例如砸碎实验中的氯校正相关图解；
(3) IsoplotR 非常适合绘图，但缺乏对 <sup>40</sup>Ar/<sup>39</sup>Ar 数据校正和相对复杂计算的支持，例如更改参数重新计算等。
此外，ArArCALC 和 Isoplot/IsoplotR的等时线回归方式有所不同。

WebArAr 的主要目的是跟进 <sup>40</sup>Ar/<sup>39</sup>Ar 定年新的需求，
平衡 ArArCALC 和 IsoplotR 的使用体验，以服务社区。

## 使用

* 请访问 http://www.webarar.net 访问本应用程序，可将本域名加入收藏夹。
* 详细使用指导请参阅 [教程](/static/readme/Tutorial_zh_CN.md)。
* （可选）在您的计算机上部署并启动 WebArAr 以供离线使用。请参阅 [部署](/static/readme/Deployment_zh_CN.md).
* （可选）用任意 Python IDE 引用 ArArPy 以使用处理处理功能。请参阅 [ArArPy](#ararpy).
<!-- * [Video examples]() -->


## 功能
- [x] 导入
    - [x] 质谱仪原始文件
    - [x] ArArCALC 项目文件 （后缀 .age）
    - [x] ArArCALC 导出文件 （后缀 .xls）
    - [x] 手动输入
- [x] 原始数据处理
    - [x] 外推零时刻截距值
    - [x] 本底校正
    - [x] 质量歧视校正
    - [x] 衰变校正
    - [x] 干扰核反应校正
- [ ] 计算
    - [x] 年龄计算
        - [x] 常规年龄计算
        - [x] Min 计算公式
        - [x] Renne 年龄标定
    - [ ] 等时线拟合
        - [x] 正反等时线
        - [x] 氯相关性图解
        - [x] York 考虑误差相关性的加权回归
        - [ ] 鲁棒回归
        - [ ] 其他回归方法
    - [x] 三维氯校正图解
    - [x] 年龄谱
        - [x] 由等时线推导的初始比值再校正年龄坪
        - [x] 坪年龄
    - [x] 卡方检测值和 P 值
    - [x] MSWD 
- [x] 界面、数据表和图解
    - [x] 交互式多表格和图解
- [x] 导出
    - [x] XLS：EXCEL 文件，包含所有数据表和图表（除三维图）
    - [x] PDF：可由Adobe Acrobat / Illustrator / CorelDRAW 打开根据需要再编辑
    - [x] SVG：轻量化
    - [ ] 三维图尚不能导出

## 更新记录

请查看 [更新记录](CHANGE_LOG.md)

## 引用 WebArAr 或 ArArPy


## 参考资料

