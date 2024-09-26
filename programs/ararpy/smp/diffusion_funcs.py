#  Copyright (C) 2024 Yang. - All Rights Reserved

# !/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2024 Yang 
# ararpy - diffusion_funcs
# ==========================================
#
#
# 
"""

import os
import shutil
import string

import numpy as np
from .sample import Sample
import ararpy as ap
import matplotlib as mpl
import scipy.stats as stats
import math
from scipy.special import comb
from datetime import datetime as dt
import re
import time
import ctypes
import gc
import random

mpl.use('TkAgg')
import matplotlib.pyplot as plt

np.set_printoptions(precision=18, threshold=10000, linewidth=np.inf)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class DiffSample:
    def __init__(self, smp: Sample = None, name: str = None, **kwargs):

        self.loc = "D:\\PythonProjects\\ararpy_package\\ararpy\\examples"

        for key, val in kwargs.items():
            setattr(self, key, val)

        os.makedirs(self.loc, exist_ok=True)

        if smp is not None:
            self.smp = smp
            self.sname = self.smp.name()

            self.sequence = self.smp.sequence()
            self.ni = self.sequence.size  # sequence number

            # self.telab = np.linspace(600, 1500, self.ni, dtype=np.float64)
            self.telab = np.array(self.smp.TotalParam[124], dtype=np.float64)

            self.telab = self.telab + 273.15
            # self.tilab = np.array([15*60 for i in range(self.ni)], dtype=np.float64)
            self.tilab = np.array(self.smp.TotalParam[123], dtype=np.float64)  # in minute
            self.a39 = np.array(self.smp.DegasValues[20], dtype=np.float64)
            self.sig39 = np.array(self.smp.DegasValues[21], dtype=np.float64)
            self.f = np.cumsum(self.a39) / self.a39.sum()
            self.f = np.where(self.f >= 1, 0.9999999999999999, self.f)
            # self.f[-1] = 0.999999999
            # self.f = np.insert(self.f, 0, 0)
            self.ya = np.array(self.smp.ApparentAgeValues[2], dtype=np.float64)
            self.sig = np.array(self.smp.ApparentAgeValues[3], dtype=np.float64)

            read_from_file = kwargs.get('read_from_file', False)
            if read_from_file:
                self.file_age_in = open(os.path.join(self.loc, f"{self.sname}_age.in"), "w")
                self.file_sig_in = open(os.path.join(self.loc, f"{self.sname}_sig.in"), "w")
                self.file_tmp_in = open(os.path.join(self.loc, f"{self.sname}_tmp.in"), "w")
                self.file_fj_in = open(os.path.join(self.loc, f"{self.sname}_fj.in"), "w")
                self.file_a39_in = open(os.path.join(self.loc, f"{self.sname}_a39.in"), "w")

                self.file_age_in.writelines("\n".join([f"  {self.f[i] * 100}  {self.ya[i]}" for i in range(self.ni)]))
                self.file_sig_in.writelines("\n".join([f"{self.sig[i]}" for i in range(self.ni)]))
                self.file_tmp_in.writelines(f"{str(self.ni)}\n")
                self.file_tmp_in.writelines("\n".join([f"{self.telab[i]}\n{self.tilab[i]}" for i in range(self.ni)]))
                self.file_fj_in.writelines("\n".join([f"{self.f[i]}" for i in range(self.ni)]))
                self.file_a39_in.writelines("\n".join([f"  {self.a39[i]}  {self.sig39[i]}" for i in range(self.ni)]))

                self.file_age_in.close()
                self.file_sig_in.close()
                self.file_tmp_in.close()
                self.file_fj_in.close()
                self.file_a39_in.close()


        elif name is not None:
            self.sname = name
        else:
            raise ValueError("Sample not found")

        self.pi = 3.141592654
        self.nloop = 1
        self.ngauss = 10
        self.zi = [0.]
        self.b = 8
        self.imp = 2
        self.acut = 0.5
        self.dchmin = 0.01
        self.ncons = 0
        self.ndom = 8
        self.mdom = 8
        self.iset = 0
        self.gset = 0
        self.wt = []


class DiffArrmultiFunc(DiffSample):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.file_output_par = open(os.path.join(self.loc, f"{self.sname}.par"), "w")
        self.file_output_ame = open(os.path.join(self.loc, f"{self.sname}.ame"), "w")
        # self.file_output_mch = open(os.path.join(self.loc, f"{self.sname}_mch-out.dat"), "w")
        # self.file_output_mages = open(os.path.join(self.loc, f"{self.sname}_mages-out.dat"), "w")
        # self.file_output_agesd = open(os.path.join(self.loc, f"{self.sname}_ages-sd.samp"), "w")
        # self.file_output_mchisq = open(os.path.join(self.loc, f"{self.sname}_mchisq.dat"), "w")
        # self.file_output_mpar = open(os.path.join(self.loc, f"{self.sname}_mpar.out"), "w")

        # self.file_tmp_in = open(os.path.join(self.loc, f"{self.sname}_tmp.in"), "r")
        # self.file_fj_in = open(os.path.join(self.loc, f"{self.sname}_fj.in"), "r")
        # self.file_a39_in = open(os.path.join(self.loc, f"{self.sname}_a39.in"), "r")

        # self.ni = int(self.file_tmp_in.readline())  # sequence number
        self.ni = 100
        self.nimax = self.ni
        self.telab = []
        self.tilab = []
        self.f = [0]  # ar39%, array(ni)
        self.a39 = []  # ar39, array(ni - 1)
        self.sig39 = []  # sigma of ar39, array(ni - 1)

        # for i in range(self.ni):
        #     self.telab.append(float(self.file_tmp_in.readline()))  # heating temperature in Kelvin
        #     self.tilab.append(float(self.file_tmp_in.readline()) * 60)  # heating time in second.
        #     self.f.append(float(self.file_fj_in.readline()))
        #     try:
        #         [_, v, sv] = self.file_a39_in.readline().split('  ')
        #     except ValueError:
        #         continue
        #     else:
        #         self.a39.append(float(v))
        #         self.sig39.append(float(sv))
        #
        # self.file_fj_in.close()
        # self.file_tmp_in.close()
        # self.file_a39_in.close()

        print(f"{self.sname = }")
        print(f"{self.a39 = }")
        print(f"{self.sig39 = }")
        print(f"{self.f = }")
        print(f"{self.telab = }")
        print(f"{self.tilab = }")

    def main(self):

        print(f"\n======================================")
        print(f"Run Arrmulti Main | ")
        print(f"======================================")

        print(f"{self.sname = }")
        print(f"{self.a39 = }")
        print(f"{self.sig39 = }")
        print(f"{self.f = }")
        print(f"{self.telab = }")
        print(f"{self.tilab = }")

        output_lines = ""

        self.ochisq = 0
        mmax = 20
        self.da = np.zeros(mmax, dtype=np.float64)
        da = np.zeros(mmax, dtype=np.float64)
        self.atry = np.zeros(mmax, dtype=np.float64)
        self.beta = np.zeros(mmax, dtype=np.float64)

        ns = 200
        r = 1.987E-3
        pi = 3.141592654
        ee = 0.4342944879
        amax = 0

        xlogr = [0]
        # dtr2 = [math.pi * (fi / 4) ** 2 if fi <= 0.5 else math.log((1 - fi) * math.pi ** 2 / 8) / (- math.pi ** 2) for
        #         fi in self.f[1:]]
        # dtr2.insert(0, 0)
        # xlogd = [np.log10((dtr2[i + 1] - dtr2[i]) / self.tilab[i] * self.imp ** 2) for i in range(0, len(dtr2) - 1)]
        xlogd = self.xlogd
        tinv = [1 / i * 10000 for i in self.telab]
        self.nimax = self.ni  # the first sequence index great than 1100 celsius degree
        for i in range(self.ni):
            if self.nimax == self.ni and self.telab[i] > 1373:
                self.nimax = i

        # wt = self.errcal()
        wt = self.wt

        wf = []
        sumwf = 0
        for i in range(self.ni):
            wf.append(1 / np.sqrt(self.f[i + 1] - self.f[i]))
            sumwf += wf[i]



        for i in range(self.ni):
            # print(f"{wf[i] = }")
            wf[i] = wf[i] / sumwf

        e, sige, ordi, sigo = self.param(tinv=tinv, wt=wt, xlogd=xlogd)

        print(self.sname)
        print(f'E={e} +- {sige} Ordinate={ordi} +- {sigo}')

        self.file_output_par.writelines(f'{self.sname}\nE={e} +- {sige} Ordinate={ordi} +- {sigo}\n')

        slop = e * ee / (r * 10000)
        xro = (ordi - slop * tinv[self.nimax - 1] - xlogd[self.nimax - 1]) / 2 * (1 + (1 - self.f[self.nimax]) / 2)

        e0 = e
        ord0 = ordi
        self.ni = self.nimax

        ### here starts loop for gaussian E,

        nca = 20
        zi = [0]
        ndom = 8
        na = 2 * ndom - 1
        a1 = np.zeros(na + 1, dtype=np.float64)
        a2 = np.zeros(na + 1, dtype=np.float64)
        auxal = np.zeros([na + 1, na + 1], dtype=np.float64)
        auxa1 = np.zeros(na + 1, dtype=np.float64)
        auxa2 = np.zeros(na + 1, dtype=np.float64)
        iseed = -3
        ckchisq = 1.0e30
        ckchin = 1.0e30
        dchmin = 0.01
        mct = 0
        ncicle = 0
        chisq = 100000
        kctotal = 0
        alpha = np.zeros([nca, nca], dtype=np.float64)
        alpha[:nca, :nca] = 0.0
        covar = np.zeros([na, na], dtype=np.float64)
        covar[:na, :na] = 0.0

        zi = self.zita(e, ordi)

        print(f"{zi = }")

        self.generator = Ran1Generator(idum=iseed)

        nnnnnn = 0

        count = 0
        count2 = 0
        to_break = False

        while True:

            nnnnnn += 1

            a1, a2 = self.guess(ndom, a1, a2, xro, self.generator.idum)

            continue_mark = 0

            if mct > 30:
                if ncicle > 0:
                    ncicle = 4
                amax = 0.
                mct = 0
                chisq = 1.0e30

                continue

            nc = 0
            lista = np.zeros(na, dtype=np.float64)
            for j in range(na):
                lista[j] = j
            mfit = na
            if self.ncons == 1:
                mfit = na - 1
            alamda = -1
            kc = 0.
            ch = -1.
            alam = 0.001

            while True:

                # print(f"\n======================================")
                # print(f"Before run mrqmin | inputs: ")
                # print(f"======================================")
                #
                # print(f"{zi = }")
                # print(f"{self.f = }")
                # print(f"{wf = }")
                # print(f"{self.ni = }")
                # print(f"{a2 = }")
                # print(f"{na = }")
                # print(f"{lista = }")
                # print(f"{mfit = }")
                # print(f"{covar = }")
                # print(f"{alpha = }")
                # print(f"{chisq = }")
                # print(f"{alamda = }")

                amax, chisq, alamda, covar, alpha, a2, y = self.mrqmin(
                    x=zi, y=self.f, sig=wf, ndata=self.ni, a=a2, ma=na, lista=lista, mfit=mfit, covar=covar,
                    alpha=alpha, chisq=chisq, alamda=alamda
                )

                kctotal = kctotal + 1

                for j in range(0, na, 2):
                    if a2[j + 1] < -14:
                        amax = -1

                for j in range(0, na, 2):
                    for k in range(0, na, 2):
                        if j == k:
                            continue
                        if a2[j] == a2[k]:
                            amax = -1

                if amax == -1:
                    mct += 1
                    continue_mark = 1
                    break

                if alam > alamda:
                    nc = 0
                else:
                    nc += 1
                    if nc <= 50:
                        ch = chisq
                        alam = alamda
                        continue
                    mct += 1
                    continue_mark = 1
                    break

                chisqn = chisq
                if chisq > 1.:
                    chisqn = 1.

                dchisq = abs((chisq - ch) / chisqn)
                kc += 1

                # print(f"{kc = }, {dchisq = }, {dchmin = }, {amax = }")
                print(f'# dom = {ndom}, Isteps = {kc}, mct = {mct}, nc = {nc}, chisq = {chisq}')

                # if count == 1 and count2 == 7:
                #     wuyang = input("continue")
                # wuyang = input("continue")

                if (dchisq >= dchmin and kc <= 100) or kc < 5:
                    ch = chisq
                    alam = alamda
                    continue
                else:
                    break

            if continue_mark == 1:
                continue
            count2 += 1
            output_lines += f'\n{nnnnnn}# dom = {ndom}, Isteps = {kc}, mct = {mct}, nc = {nc}, chisq = {chisq}'
            print(output_lines)
            self.file_output_par.writelines(f"dom = {ndom}, Isteps = {kc}, mct = {mct}, nc = {nc}, chisq = {chisq}\n")
            # wuyang = input("continue")

            if ckchisq > chisq:
                for j in range(na + 1):
                    auxa2[j] = a2[j]
                    for k in range(na + 1):
                        auxal[j, k] = alpha[j, k]  # 注意二维数组的索引, alpha是一个对称矩阵
                auxna = na
                ckchisq = chisq

            if ckchin > chisq:

                y, dyda = self.funcs(zi[1], a2, na, auxa1)
                if amax == -1:
                    break
                ckchin = chisq

            if ncicle < 4:
                ncicle = ncicle + 1
            else:
                auxa1, a2, da = self.sort3(auxa1[:na + 1], a2[:na + 1], da[:na + 1])
                ndom -= 1
                mct = 0
                ncicle = 0
                ckchin = 1e30
                sumc = 0
                for j in range(0, na, 2):
                    sumc += auxa1[j + 1]

                if ndom == self.mdom - 1:
                    for j in range(0, int(auxna + 1)):
                        a2[j] = auxa2[j]
                        for k in range(0, int(auxna + 1)):
                            alpha[j, k] = auxal[j, k]  # 注意二维数组的索引
                    na = auxna
                    mfit = na
                    if self.ncons == 1:
                        mfit = na - 1
                    amax = 0

                    # go to 72

                    alamda = 0
                    ndom = int((na + 1) / 2)

                    amax, chisq, alamda, covar, alpha, a2, y = \
                        self.mrqmin(x=zi, y=self.f, sig=wf, ndata=self.ni, a=a2, ma=na,
                                    lista=lista, mfit=mfit, covar=covar, alpha=alpha,
                                    chisq=chisq, alamda=alamda, amax=amax)

                    if amax == -1:
                        mct += 1
                        continue

                    fmod = np.zeros(ns, dtype=np.float64)
                    for nt in range(self.ni):
                        y, dyda = self.funcs(zi[nt], a2, na, a1)
                        fmod[nt] = y
                        if amax == -1:
                            continue

                    a1, a2, da = self.sort3(a1[:na + 1], a2[:na + 1], da[:na + 1])

                    rpmax = a1[na - 1]
                    xlog = ordi - 2 * np.log10(rpmax)

                    self.file_output_ame.writelines(f"{ndom}\n")

                    sc = 0
                    kd = 8

                    orde = np.zeros(20, dtype=np.float64)
                    for j in range(0, na + 1, 2):

                        self.file_output_ame.writelines(f"{e}\n")

                        orde[j] = xlog - 2 * np.log10(a1[j] / rpmax)

                        self.file_output_ame.writelines(f"{orde[j]}\n")
                        self.file_output_ame.writelines(f"{a1[j + 1]}\n")

                        output_lines += f'\n{int((j + 1 + 1) / 2)}, {a1[j + 1]}, {a1[j] / rpmax}'
                        self.file_output_par.writelines(f"{int((j + 1 + 1) / 2)}, {a1[j + 1]}, {a1[j] / rpmax}\n")

                        if sc + a1[j + 1] > self.f[self.nimax] > sc:
                            kd = int((j + 1 + 1) / 2)

                        sc += a1[j + 1]

                    output_lines += f'\n{ckchisq}'
                    print(output_lines)
                    self.file_output_par.writelines(f"{ckchisq}\n")

                    slop = e * ee / 10000. / r

                    self.file_output_ame.writelines(f"{slop}\n")
                    self.file_output_ame.writelines(f"{ordi}\n")

                    dzx = np.zeros(ns, dtype=np.float64)
                    dzx, _ = self.arr(e, ordi, dzx, fmod, self.f, self.telab, self.tilab, xlogd)

                    chisq2 = 0.
                    noutlier = 0

                    for i in range(self.nimax):
                        dy1 = abs((xlogd[i] - dzx[i]) / wt[i])
                        if dy1 < 4:
                            chisq2 = chisq2 + dy1 ** 2
                        else:
                            noutlier += 1

                    q = gammq(0.5 * (self.nimax - 2), 0.5 * chisq2)

                    ke = 0
                    # print(f"{self.sname = }, {e = }, {sige = }, {ordi = }, {sigo = }, {ke = }, {chisq2 = }, {q = }, {self.nimax}, {noutlier = }")

                    self.file_output_ame.writelines(f"&\n")

                    if self.nloop <= self.ngauss:

                        output_lines += f'\n{kctotal = }'
                        self.file_output_par.writelines(f"{kctotal = }\n\n")

                        kctotal = 0
                        e, ordi = self.stats(e0, sige, ord0, sigo, self.generator.idum)

                        output_lines += f'\n{e = }, {ordi = }'

                        print(output_lines)
                        self.file_output_par.writelines(f"{e = }, {ordi = }\n")

                        # go to self.zita()

                        zi = self.zita(e, ordi)
                        ckchisq = 1.0e30
                        ckchin = 1.0e30
                        mct = 0
                        nnnnnn = 0

                        count += 1

                        if self.nloop == self.ngauss:
                            break
                        self.nloop += 1

                        continue
                    break
                break

        self.file_output_par.close()
        self.file_output_ame.close()

        return e, sige, ordi, sigo

    def errcal(self):

        ns = 200
        r = 1.987E-3
        ee = 0.4342944819
        sigt0 = 90.
        a0 = -0.19354
        a1 = -0.62946
        a2 = 0.13505
        a3 = -0.01528

        f1 = [0]

        sumat = sum(self.a39)
        sigsm = [i / sumat for i in self.sig39]
        siga = [self.sig39[i] / self.a39[i] for i in range(self.ni)]

        an1 = self.pi ** 2
        sigat = 0.
        swt = 0.
        sigzit = [0.]
        sigf = [0]

        for i in range(self.ni):
            sigat += sigsm[i] ** 2
            sigf.append(sigat)

        for i in range(1, self.ni + 1):
            sigzit.append(0)
            if self.f[i] <= 0.5:
                fp = self.f[i] + self.f[i - 1]
                as1 = 1. / fp ** 2 - 2. / fp
                as2 = (self.f[i] ** 2 - 2 * self.f[i] * (self.f[i] ** 2 - self.f[i - 1] ** 2)) / fp ** 2
                sigzit[i] = 4. * (sigat + sigf[i - 1] * as1 + siga[i - 1] ** 2 * as2)
            else:
                dzit2 = (np.log((1 - self.f[i]) / (1 - self.f[i - 1])) / an1) ** 2
                as1 = ((self.f[i] - self.f[i - 1]) / an1) ** 2 / (1 - self.f[i - 1]) ** 2
                sigzit[i] = ((sigat - sigf[i]) / (1 - self.f[i]) ** 2 + siga[i - 1] ** 2) * as1
                sigzit[i] = sigzit[i] / dzit2

        for i in range(self.ni):
            sigt = (sigt0 / self.tilab[i]) ** 2
            self.wt.append(ee * (sigt + sigzit[i + 1]) ** 0.5)
            swt = swt + self.wt[i]
            rate = (sigzit[i + 1] / sigt) ** 0.5

        return self.wt

    def param(self, tinv, wt, xlogd, nstop=20, r=1.987E-3, pi=3.141592654, ee=0.4342944879, dtp=5.0):

        # print(f"\n======================================")
        # print(f"Run param")
        # print(f"======================================\n")
        # print(f"{tinv = }")
        # print(f"{wt = }")
        # print(f"{xlogd = }")

        telab = self.telab
        ni = self.ni
        ns = 200
        f = np.zeros(ns + 1, dtype=np.float64)
        telab = np.array(telab)
        tilab = np.zeros(ns, dtype=np.float64)
        xlogd = np.array(xlogd, dtype=np.float64)
        sig39 = np.zeros(ns, dtype=np.float64)
        xlogr = np.zeros(ns + 1, dtype=np.float64)
        a39 = np.zeros(ns, dtype=np.float64)
        acut = 0.0
        b = 0.0
        sige = 0.0
        sigo = 0.0
        qmax = 0.0
        chisqe = 0.0
        ni = int(ni)
        imp = 0
        nimax = 0
        ke = 0

        iflag2 = 0
        nst = nstop  # nstop = 20
        y = np.zeros(ns, dtype=np.float64)
        alog = np.zeros(ns, dtype=np.float64)
        x1 = np.zeros(ns, dtype=np.float64)
        y1 = np.zeros(ns + 1, dtype=np.float64)
        wty = np.zeros(ns, dtype=np.float64)
        wtx = np.zeros(ns, dtype=np.float64)

        if ni < nstop:
            nst = ni

        ki = 0

        while True:
            print(f"{nst = }")
            qmaxk = 0.0
            qmax = 1.0
            sx1 = 0.0

            for j in range(1, 4):
                x1[j - 1] = tinv[ki + j - 1]
                sx1 += x1[j - 1]
                y1[j - 1] = xlogd[ki + j - 1]
                wty[j - 1] = wt[ki + j - 1]
                wtx[j - 1] = 10000.0 * dtp / telab[ki + j - 1] ** 2

            for k in range(4, nst + 1):
                x1[k - 1] = tinv[ki + k - 1]
                sx1 += x1[k - 1]
                y1[k - 1] = xlogd[ki + k - 1]
                wty[k - 1] = wt[ki + k - 1]
                wtx[k - 1] = 10000.0 * dtp / telab[ki + k - 1] ** 2

                if x1[k - 1] == sx1 / k:
                    continue

                ncont = 1
                for j in range(2, k + 1):
                    ks = 0
                    for j1 in range(1, j):
                        if x1[j - 1] == x1[j1 - 1]:
                            ks = 1
                    if ks == 0:
                        ncont += 1
                    # print(f"{ks = }, {ncont = }, {x1[j - 1] = }")

                # print(x1[:k])
                # print(y1[:k])
                # print(x1)
                # print(y1)

                # a, siga, bf, sigb, mswd, conv, Di, _, r2, chi2, p_value, s = ap.calc.regression.york2(x1[:k], wtx[:k], y1[:k], wty[:k], [0 for i in x1[:k]])

                # print("==== fit over =====")
                # print(f"{a = }, {siga = }, {bf = }, {sigb = }, {chi2 = }, {p_value = }")

                a, bf, siga, sigb, chi2, q = fit(x1[:k], y1[:k], wtx[:k], wty[:k])
                # a: intercept, bf : slope

                print("==== fit over =====")
                line = f"{k = }, {a = }, {siga = }, {bf = }, {sigb = }, {chi2 = }, {q = }, {ncont = }"
                print(line)
                # with open(r"C:\Users\Young\Desktop\fit_results.txt", 'a+') as f:
                #     f.writelines(line + '\n')

                if q / qmax < 1.e-10 and k > 8 and iflag2 == -1:
                    break

                y[k - 1] = -r * bf * 10000.0 / ee
                alog[k - 1] = a
                sige1 = r * sigb * 10000.0 / ee
                qs = k * q

                if qs > qmaxk and ncont >= 3:
                    iflag2 = -1
                    ke = k
                    if qs > qmaxk:
                        qmaxk = qs
                    qmax = q
                    chisqe = chi2
                    sige = sigb * r * 10000.0 / ee
                    sigo = siga

                    e = y[k - 1]
                    ordi = alog[k - 1]

                print(f"{ki = }, {qs = }, {qmaxk = }, {ncont = }")

            if ki == 0 and qmax < 0.05:
                ki = 1
            else:
                break

        return e, sige, ordi, sigo

    def zita(self, e, ordi, nca=20, ns=200, r=1.987E-3, pi=3.141592654, ee=0.4342944879):
        zi = np.zeros(ns, dtype=np.float64)
        imp = 2
        d0 = 10 ** ordi / (imp ** 2)
        for i in range(1, self.ni + 1):
            zi[i] = d0 * self.tilab[i - 1] * np.exp(-1 * e / r / self.telab[i - 1]) + zi[i - 1]
        return zi

    def guess(self, ndom, a1, a2, xro, iseed):

        # a1 = np.zeros(2 * ndom, dtype=np.float64)
        # a2 = np.zeros(2 * ndom, dtype=np.float64)

        na = 2 * ndom
        sum = 0.0

        # print(f"\n======================================")
        # print(f"Run guess")
        # print(f"======================================")
        # print(f"{ndom = }, {xro = }, {iseed = }, {na = }")
        # print(f"{a1 = }")
        # print(f"{a2 = }")

        # Definition of volume concentration
        for j in range(0, na, 2):
            a1[j + 1] = 1.0 + 10.0 * self.generator.ran1()
            sum += a1[j + 1]

        # Normalization of volume concentration
        for j in range(0, na, 2):
            a1[j + 1] = a1[j + 1] / sum

        # Definition of sizes (start with random order numbers greater to smaller)
        sum = 0.0
        for j in range(0, na - 2, 2):
            sum = 1.0 + 10.0 * self.generator.ran1() + sum
            a1[na - 2 - j - 2] = sum

        # Normalized to max log(r/ro) value xro, a1(1)=xro
        for j in range(0, na - 2, 2):
            a1[j] = a1[j] / sum * xro

        sum = a1[na - 1] + a1[na - 3]
        for j in range(2, na - 3, 2):
            a1[j] = a1[j] - np.log10(sum)
            sum = sum + a1[na - (j + 1) - 2]

        ro = 10.0 ** a1[0]

        for j in range(2, na - 3, 2):
            a2[j] = a1[0] - a1[na - j - 2]

        for j in range(2, na - 3, 2):
            a1[j] = a2[j]

        a1[na - 2] = np.log10(a1[na - 1])

        for j in range(0, na - 3, 2):
            a1[j] = a1[j + 1] / (10.0 ** a1[j] - 10.0 ** a1[j + 2])

        a1[na - 2] = 1.0

        # print(f"{a1}")

        nloop = 0
        while True:
            ncont = 0
            nloop += 1
            for j in range(0, na - 3, 2):
                rom = 0.0
                if a1[j] > 1.0:
                    raise ValueError("a1(j) > 1.")
                if a1[j + 2] < a1[j]:
                    ncont = 0
                    for k in range(j, j + 3, 2):
                        rom += a1[k + 1] / a1[k]
                    a1[j + 2] = a1[j]
                    a1[j] = a1[j + 1] / (rom - a1[j + 3] / a1[j + 2])
                else:
                    ncont += 1

            if nloop > 30:
                raise ValueError("nloop greater than 30 on guess")
            if ncont >= (ndom - 1):
                break

        sumro = 0.0
        for j in range(0, na - 1, 2):
            sumro += a1[j + 1] / a1[j]

        # Calculation of A2
        for j in range(0, na - 1, 2):
            a2[j] = 2.0 * np.log(a1[j] * ro)
            z = 2.0 * a1[j + 1] - 1.0
            a2[j + 1] = 0.5 * np.log((z + 1.0) / abs(z - 1.0))


        # print(f"\n======================================")
        # print(f"Return guess")
        # print(f"======================================\n")
        # print(f"{a1 = }")
        # print(f"{a2 = }")

        return a1, a2

    def mrqmin(self, x, y, sig, ndata, a, ma, lista, mfit, covar, alpha, chisq, alamda, amax=0):

        mmax = 20

        # print(f"\n======================================")
        # print(f"Run mrqmin | inputs: ")
        # print(f"======================================")
        #
        # print(f"{x = }")
        # print(f"{y = }")
        # print(f"{sig = }")
        # print(f"{self.da = }")
        # print(f"{self.atry = }")
        # print(f"{self.beta = }")
        # print(f"{a = }")
        # print(f"{alpha = }")

        x = x[:ndata + 1]
        y = y[:ndata + 1]
        sig = sig[:ndata + 1]

        for j in range(0, ma, 2):
            if abs(2 * a[j]) > amax:  # 扩散与尺寸的两倍的最大值，相当于直径 (?)
                amax = abs(2 * a[j])

        if amax > 30:
            amax = 30

        if alamda < 0:
            iseed = 1
            kk = mfit + 1
            for j in range(0, ma):
                ihit = 0
                for k in range(1, mfit + 1):
                    if lista[k - 1] == j:
                        ihit += 1
                if ihit == 0:
                    lista[kk - 1] = j
                    kk += 1
                elif ihit > 1:
                    raise ValueError('ERROR(MRQMIN): improper permutation in lista')

            if kk != (ma + 1):
                raise ValueError('ERROR(MRQMIN): improper perm. in lista')

            alamda = 0.001

            # print(f"\n======================================")
            # print(f"Before run mrqcof | inputs: ")
            # print(f"======================================")
            #
            # print(f"{x = }")
            # print(f"{y = }")
            # print(f"{sig = }")
            # print(f"{ndata = }")
            # print(f"{a = }")
            # print(f"{ma = }")
            # print(f"{lista = }")
            # print(f"{mfit = }")
            # print(f"{alpha = }")
            # print(f"{self.beta = }")
            # print(f"{amax = }")

            chisq, alpha, self.beta, a = self.mrqcof(x, y, sig, ndata, a, ma, lista, mfit, alpha, self.beta,
                                                            amax)

            # print(f"{alpha = }")

            if amax == -1:
                return amax, chisq, alamda, covar, alpha, a, y

            self.ochisq = chisq
            for j in range(ma):
                self.atry[j] = a[j]

        for j in range(1, mfit + 1):
            for k in range(1, mfit + 1):
                covar[j - 1, k - 1] = alpha[j - 1, k - 1]
            covar[j - 1, j - 1] = alpha[j - 1, j - 1] * (1 + alamda)
            self.da[j - 1] = self.beta[j - 1]


        # print(f"\n======================================")
        # print(f"Before run gaussj | inputs: ")
        # print(f"======================================")
        #
        # print(f"{covar = }")
        # print(f"{mfit = }")
        # print(f"{self.da = }")
        # print(f"{amax = }")


        """
        ### 重要：这里gaussj由于浮点数累乘，fortran与python有结果偏差，
        ### Python保留了十六位有效数字，而fortran保留了十七位，进而影响了后续self.atry, alpha, covar等。
        """

        amax = self.gaussj(covar, mfit, self.da, amax=amax)  # (a, n, b)

        # print(f"{self.da = }")
        # print(f"{amax = }")

        # self.da = np.array([
        #     -0.74462339237294706, -5.4325676972901193E-002, 0.11264123464026662, -0.34299477191764405,
        #     -0.58013840179828902, -0.26581668757842275, -0.34280431209811241, -0.25866937785643079,
        #     0.31231250958181944, -0.37302348875611602, -0.72941880170200390, -0.39768996285870495,
        #     4.4803941640740721, 1.0107355396065272, -14.263407247136517, 0.0000000000000000,
        #     0.0000000000000000, 0.0000000000000000, 0.0000000000000000, 0.0000000000000000,
        # ])

        if amax == -1:
            return amax, chisq, alamda, covar, alpha, a, y

        for j in range(0, mfit, 2):
            if abs(self.da[j]) > 8:
                self.da[j] = 8 * np.sign(self.da[j])
            if abs(self.da[j + 1]) > 3:
                self.da[j + 1] = 3 * np.sign(self.da[j + 1])

        if alamda == 0:
            self.covsrt(covar, ma, lista, mfit)
            return amax, chisq, alamda, covar, alpha, a, y

        while True:

            go_to_21 = False
            sum = 0

            for j in range(0, mfit):
                self.atry[int(lista[j])] = a[int(lista[j])] + self.da[j]
                if j % 2 != 0 and self.atry[int(lista[j])] < -5:
                    self.atry[int(lista[j])] = -5
                if j % 2 == 0 and abs(self.atry[int(lista[j])]) > 14:
                    self.atry[int(lista[j])] = 14 * np.sign(self.atry[int(lista[j])]) + self.generator.ran1()

            if ma != mfit:
                for k in range(0, mfit - 1, 2):
                    if self.atry[k] >= self.atry[ma - 1] or abs(self.atry[k]) > amax:
                        self.da[k] /= 2
                        go_to_21 = True
                        break
                if go_to_21:
                    continue
            else:
                for j in range(0, mfit, 2):
                    if abs(self.atry[j]) > amax:
                        self.da[j] /= 2
                        go_to_21 = True
                        break
                if go_to_21:
                    continue

            for k in range(1, mfit, 2):
                sum += (1 + np.tanh(self.atry[k])) / 2
            # print(f"{sum = }")
            if sum >= 1:
                for k in range(1, mfit + 1, 2):
                    self.da[k] /= 2
                continue

            break

        # print(f"\n======================================")
        # print(f"Before second run mrqcof | inputs: ")
        # print(f"======================================")
        #
        # print(f"{x = }")
        # print(f"{y = }")
        # print(f"{sig = }")
        # print(f"{ndata = }")
        # print(f"{self.atry = }")
        # print(f"{ma = }")
        # print(f"{lista = }")
        # print(f"{mfit = }")
        # print(f"{covar = }")
        # print(f"{self.da = }")
        # print(f"{amax = }")

        chisq, covar, _, __ = self.mrqcof(x, y, sig, ndata, self.atry, ma, lista, mfit, covar, self.da, amax)

        # print(f"{covar = }")

        if amax == -1:
            return amax, chisq, alamda, covar, alpha, a, y

        if chisq <= self.ochisq:
            alamda = 0.1 * alamda
            self.ochisq = chisq
            for j in range(mfit):
                for k in range(mfit):
                    alpha[j, k] = covar[j, k]
                self.beta[j] = self.da[j]
                a[int(lista[j])] = self.atry[int(lista[j])]
        else:
            alamda = 10 * alamda
            chisq = self.ochisq

        # print(f"\n======================================")
        # print(f"Return mrqmin | outputs: ")
        # print(f"======================================\n")
        #
        # print(f"{amax = }")
        # print(f"{chisq = }")
        # print(f"{alamda = }")
        # print(f"{covar = }")
        # print(f"{alpha = }")
        # print(f"{a = }")
        # print(f"{y = }")
        # print(f"{self.da = }")
        # print(f"{self.atry = }")
        # print(f"{self.beta = }")

        return amax, chisq, alamda, covar, alpha, a, y

    def mrqcof(self, x, y, sig, ndata, a, ma, lista, mfit, alpha, beta, amax):

        # print(f"\n======================================")
        # print(f"Run mrqcof")
        # print(f"======================================")
        #
        # print(f"{x = }")
        # print(f"{y = }")
        # print(f"{sig = }")
        # print(f"{ndata = }")
        # print(f"{a = }")
        # print(f"{ma = }")
        # print(f"{lista = }")
        # print(f"{mfit = }")
        # # print(f"{alpha = }")
        # print(f"{beta = }")
        # print(f"{amax = }")

        mmax = 20
        dyda = np.zeros(mmax, dtype=np.float64)
        a1 = np.zeros(mmax, dtype=np.float64)
        beta[:mfit] = 0.0

        for j in range(mfit):
            for k in range(j + 1):
                alpha[j, k] = 0

        chisq = 0.0

        chisq_list = []

        for i in range(0, ndata):
            ymod, dyda = self.funcs(x=x[i + 1], b=a, na=ma, a=a1)
            # print(f"after funcs {ymod = }, after funcs {dyda = }")
            if amax == -1:
                chisq = 1000000.0
                return chisq, alpha, beta, a

            sig2i = 1.0 / (sig[i] ** 2)
            dy = y[i + 1] - ymod
            # print(f"{y[i + 1] = }, {sig[i] = }")

            for j in range(mfit):
                wt = dyda[int(lista[j])] * sig2i
                # print(f"{dyda[int(lista[j])] = }")
                for k in range(j + 1):
                    alpha[j, k] += wt * dyda[int(lista[k])]
                beta[j] += dy * wt
                # print(f"({i}, {j}) >>> {beta[j]}")

            chisq += dy * dy * sig2i
            chisq_list.append(dy * dy * sig2i)

            # print(f"{chisq = }, {self.ochisq = }, {y[i + 1] = }, {ymod = }, {sig2i = }")
            # print(f"after funcs {chisq = }")

        # print(f"{alpha = }")
        # chisq = kahan_sum(chisq_list)

        for j in range(1, mfit):
            for k in range(j):
                alpha[k, j] = alpha[j, k]

        # print(f"\n======================================")
        # print(f"Return mrqcof")
        # print(f"======================================")
        #
        # print(f"{chisq = }")
        # print(f"{alpha = }")
        # print(f"{beta = }")
        # print(f"{a = }")
        # print(f"{ymod = }")
        # print(f"{dyda = }")

        return chisq, alpha, beta, a

    def funcs(self, x, b, na, a):

        # print(f"\n======================================")
        # print(f"Run funcs")
        # print(f"======================================")
        # print(f"{x = }")
        # print(f"{b = }")
        # print(f"{na = }")
        # print(f"{a = }")

        nmax = 21
        pi = 3.141592654

        if na == 0:
            return 0, np.zeros(na + 1, dtype=np.float64)

        y = 0.0
        as_ = 1.0
        csh = np.zeros(nmax, dtype=np.float64)
        dyda = np.zeros(na + 1, dtype=np.float64)

        for j in range(0, na, 2):
            a[j] = np.exp(b[j])
            a[j + 1] = (1.0 + np.tanh(b[j + 1])) / 2.0
            csh[j + 1] = 0.5 / np.cosh(b[j + 1]) ** 2
            as_ -= a[j + 1]

        a[na] = as_ + a[na]
        if a[na] < 1e-14:
            a[na] = 1e-14

        b[na] = np.log(a[na])

        for i in range(0, na, 2):

            arg = x / a[i] * 4.0
            if arg < 0:
                raise ValueError("arg less than zero")

            if arg <= 0.2827:
                gf = 2.0 * np.sqrt(arg / pi)
            else:
                if (pi / 2) ** 2 * arg > 80:
                    gf = 1.0
                else:
                    gf = 1.0 - 8.0 / pi ** 2 * np.exp(-(pi / 2) ** 2 * arg)

            dgf = 0.0
            for j in range(1, 50000, 2):
                arg1 = (j * pi / 2.0) ** 2 * arg
                if arg1 > 25:
                    break
                dgf += 2.0 * np.exp(-arg1)

            y += a[i + 1] * gf

            dyda[i + 1] = gf * csh[i + 1]
            dyda[i] = -a[i + 1] * dgf * arg

            # print(f"{a[i] = }")
            # print(f"{a[i + 1] = }")
            # print(f"{csh[i + 1] = }")
            # print(f"{gf = }")
            # print(f"{dgf = }")
            # print(f"{arg = }")

            a[i] = np.sqrt(a[i])

        # print(f"\n======================================")
        # print(f"Return funcs")
        # print(f"======================================")
        # print(f"{y = }")
        # print(f"{dyda = }")

        return y, dyda

    def gaussj(self, a, n, b, amax=0):

        # m = b.shape[1]

        nmax = 50
        ipiv = np.zeros(nmax, dtype=int)
        indxr = np.zeros(nmax, dtype=int)
        indxc = np.zeros(nmax, dtype=int)

        # print(f"\n======================================")
        # print(f"Run gaussj")
        # print(f"======================================")
        # print(f"{a = }")
        # print(f"{n = }")
        # print(f"{b = }")
        # print(f"{amax = }")

        for j in range(n):
            ipiv[j] = 0

        for i in range(n):

            big = 0.0
            for j in range(n):
                if ipiv[j] != 1:
                    for k in range(n):
                        if ipiv[k] == 0:
                            if abs(a[j, k]) >= big:
                                big = abs(a[j, k])
                                irow = j
                                icol = k
                        elif ipiv[k] > 1:
                            amax = -1
                            # return a, b, amax
                            return amax

            ipiv[icol] += 1
            if irow != icol:
                for v in range(n):
                    dum = a[irow, v]
                    a[irow, v] = a[icol, v]
                    a[icol, v] = dum

                for v in range(1):
                    try:
                        dum = b[v, irow]
                        b[v, irow] = b[v, icol]
                        b[v, icol] = dum
                    except IndexError:
                        dum = b[irow]
                        b[irow] = b[icol]
                        b[icol] = dum

            indxr[i] = irow
            indxc[i] = icol
            if a[icol, icol] == 0.0:
                amax = -1

                return amax

            pivinv = 1.0 / a[icol, icol]

            a[icol, icol] = 1.0
            a[icol] *= pivinv
            b[icol] *= pivinv

            """
            ### 重要：这里gaussj由于浮点数累乘，fortran与python有结果偏差，
            ### Python保留了十六位有效数字，而fortran保留了十七位，进而影响了后续self.atry, alpha, covar等。
            """

            for ll in range(n):
                if ll != icol:
                    dum = a[ll, icol]
                    a[ll, icol] = 0.0
                    a[ll, :] -= a[icol, :] * dum
                    b[ll] -= b[icol] * dum

        for l in range(n - 1, -1, -1):
            if indxr[l] != indxc[l]:
                a[:, [indxr[l], indxc[l]]] = a[:, [indxc[l], indxr[l]]]

        # print(f"\n======================================")
        # print(f"Return gaussj")
        # print(f"======================================")
        # print(f"{a = }")
        # print(f"{n = }")
        # print(f"{b = }")
        # print(f"{amax = }")

        return amax

    def covsrt(self, covar, ma, lista, mfit):
        # covar is expected to be a numpy array of shape (ncvm, ncvm)
        # lista is expected to be a numpy array of shape (mfit,)

        # Step 1: Zero out the upper triangle
        for j in range(ma - 1):
            for i in range(j + 1, ma):
                covar[i, j] = 0.0

        # Step 2: Reorganize the covariance matrix
        for i in range(mfit - 1):
            for j in range(i + 1, mfit):
                if lista[j] > lista[i]:
                    covar[int(lista[j]), int(lista[i])] = covar[i, j]
                else:
                    covar[int(lista[j]), int(lista[i])] = covar[i, j]

        # Step 3: Swap and reset diagonal elements
        swap = covar[0, 0]
        for j in range(ma):
            covar[0, j] = covar[j, j]
            covar[j, j] = 0.0

        covar[int(lista[0]), int(lista[0])] = swap

        for j in range(1, mfit):
            covar[int(lista[j]), int(lista[j])] = covar[0, j]

        # Step 4: Symmetrize the covariance matrix
        for j in range(1, ma):
            for i in range(j):
                covar[i, j] = covar[j, i]

        return covar

    def indexx(self, arrin):

        n = len(arrin)
        indx = np.zeros(n, dtype=int)

        for i in range(0, n, 2):
            indx[i] = i
        l = int(n / 4) * 2 + 1
        ir = n - 1

        while True:

            if l > 1:
                l -= 2
                indxt = indx[l - 1]
                q = arrin[indxt]
            else:
                indxt = indx[ir - 1]
                q = arrin[indxt]
                indx[ir - 1] = indx[1 - 1]
                ir -= 2
                if ir == 1:
                    indx[1 - 1] = indxt
                    return indx
            i = l
            j = l + l + 1
            while True:
                if j <= ir:
                    if j < ir:
                        if arrin[indx[j - 1]] < arrin[indx[j + 2 - 1]]:
                            j += 2
                    if q < arrin[indx[j - 1]]:
                        indx[i - 1] = indx[j - 1]
                        i = j
                        j = j + j + 1
                    else:
                        j = ir + 2
                    continue
                else:
                    break
            indx[i - 1] = indxt
            continue

    def sort3(self, ra, rb, rc):
        #
        # print(f"\n======================================")
        # print(f"Run sort3")
        # print(f"======================================")

        n = len(ra)
        iwksp = self.indexx(ra)

        wksp = np.empty(n)
        wksp[:] = ra[:]
        for i in range(0, n, 2):
            ra[i] = wksp[iwksp[i]]
            ra[i + 1] = wksp[iwksp[i] + 1]

        n = len(rb)
        wksp = np.empty(n)
        wksp[:] = rb[:]
        for i in range(0, n, 2):
            rb[i] = wksp[iwksp[i]]
            rb[i + 1] = wksp[iwksp[i] + 1]

        n = len(rc)
        wksp = np.empty(n)
        wksp[:] = rc[:]
        for i in range(0, n, 2):
            rc[i] = wksp[iwksp[i]]
            rc[i + 1] = wksp[iwksp[i] + 1]

        # print(f"{n = }")
        # print(f"{ra = }")
        # print(f"{rb = }")
        # print(f"{rc = }")
        # print(f"{wksp = }")
        # print(f"{iwksp = }")

        return ra, rb, rc

    def gasdev(self):
        # Using numpy's random normal distribution generator
        # return np.random.normal()
        if self.iset == 0:
            while True:
                v1 = 2 * self.generator.ran1() - 1
                v2 = 2 * self.generator.ran1() - 1
                r = v1 ** 2 + v2 ** 2

                if r >= 1:
                    continue
                else:
                    break
            fac = np.sqrt(-2 * np.log(r) / r)
            self.gset = v1 * fac
            res = v2 * fac
            self.iset = 1
        else:
            res = self.gset
            self.iset = 0

        return res

    def stats(self, xval, xerr, yval, yerr, idum):
        #
        # print(f"\n======================================")
        # print(f"Run stats")
        # print(f"======================================")
        #
        # print(f"{xval = }")
        # print(f"{xerr = }")
        # print(f"{yval = }")
        # print(f"{yerr = }")
        # print(f"{idum = }")

        rt = 0.938
        rt1 = np.sqrt(1.0 - rt ** 2)

        gnoise1 = self.gasdev()
        xran = xval + xerr * gnoise1

        gnoise2 = self.gasdev()
        yran = yval + yerr * (rt * gnoise1 + rt1 * gnoise2)

        return xran, yran

    def arr(self, e, ord, dzx, fmod, f, telab, tilab, xlogd,
            ns=200, r=1.987e-3, pi=3.141592654, ee=0.4342944879, acut=0, b=1, imp=1):

        # print(f"{e = }")
        # print(f"{ord = }")
        # print(f"{dzx = }")
        # print(f"{fmod = }")
        # print(f"{f = }")
        # print(f"{telab = }")
        # print(f"{tilab = }")
        # print(f"{xlogd = }")

        zx = np.zeros(ns + 1, dtype=np.float64)
        dzx = np.zeros(ns, dtype=np.float64)
        tab1 = "\t"

        ni = self.ni

        # INVERSION OF 39-F
        for k in range(ni):
            if fmod[k] > acut:
                zx[k + 1] = -np.log(pi ** 2 / b * (1.0 - fmod[k])) / pi ** 2
            else:
                zx[k + 1] = pi * (fmod[k] / 4.0) ** 2

        zx[0] = 0.0
        slop = e * ee / 10000.0 / r

        results_18 = []
        results_16 = []
        results_22 = []

        for k in range(ni):
            dzx[k] = np.log10((zx[k + 1] - zx[k]) / tilab[k] * imp ** 2)
            tinv = 1.0 / telab[k] * 10000.0
            xlog = (ord - slop * tinv - dzx[k]) / 2.0
            results_18.append(f"{fmod[k - 1] * 100:.8f}{tab1}{xlog:.8f}")
            results_18.append(f"{fmod[k] * 100:.8f}{tab1}{xlog:.8f}")
            results_16.append(f"{tinv:.8f}{tab1}{dzx[k]:.8f}")

        results_16.append("&")
        results_18.append("&")

        for k in range(ni):
            tinv = 1.0 / telab[k] * 10000.0
            xlogr0 = (ord - slop * tinv - xlogd[k]) / 2.0
            results_22.append(f"{f[k - 1] * 100:.8f}{tab1}{xlogr0:.8f}")
            results_22.append(f"{f[k] * 100:.8f}{tab1}{xlogr0:.8f}")

        return dzx, zx


class DiffAgemonFuncs(DiffSample):

    def __init__(self, ni=10, mmax=100, ochisq=0, **kwargs):

        self.ni = ni
        self.mmax = mmax
        self.ochisq = ochisq

        super().__init__(**kwargs)

        self.nca = 200
        self.da = np.zeros(self.ni, dtype=np.float64)
        self.beta = np.zeros(self.mmax, dtype=np.float64)
        self.atry = np.zeros(self.mmax, dtype=np.float64)

        # constants
        self.nwcy = 10
        self.ncyc = 1
        self.ntst = 1001
        self.ns = 200
        self.nmaxi = np.zeros(self.nwcy, dtype=int)
        self.nmaxo = np.zeros(self.nwcy, dtype=int)
        self.tti = np.zeros([self.nwcy, 2, self.ntst], dtype=np.float64)
        self.tto = np.zeros([self.nwcy, 2, self.ntst], dtype=np.float64)
        self.agei = np.zeros([self.nwcy, 2, self.ns], dtype=np.float64)
        self.ageo = np.zeros([self.nwcy, 2, self.ns], dtype=np.float64)

        self.file_ame_in = open(os.path.join(self.loc, f"{self.sname}.ame"), "r")  # from arrmulti

        self.file_output_mch = open(os.path.join(self.loc, f"{self.sname}_mch-out.dat"), "w")
        self.file_output_mages = open(os.path.join(self.loc, f"{self.sname}_mages-out.dat"), "w")
        self.file_output_agesd = open(os.path.join(self.loc, f"{self.sname}_ages-sd.samp"), "w")

        self.file_output_mch.close()
        self.file_output_mages.close()
        self.file_output_agesd.close()

        # parameters
        self.ns = 200
        self.nc = 100
        self.ntst = 1001
        self.mxi = 350
        self.nn = 319
        self.mfit = 10
        self.nwcy = 10
        self.nd = 10
        self.xlambd = 0.0005543
        self.a = 0
        self.perc = 0.01
        self.cht0 = 1.0e-4
        self.nrun = 5
        self.maxrun = 15
        self.nemax = 10

        read_from_file = kwargs.get('read_from_file', False)
        if read_from_file:
            self.file_age_in = open(os.path.join(self.loc, f"{self.sname}_age.in"), "r")
            self.file_sig_in = open(os.path.join(self.loc, f"{self.sname}_sig.in"), "r")
            self.file_tmp_in = open(os.path.join(self.loc, f"{self.sname}_tmp.in"), "r")

            # 读取加热温度和时间
            self.ni = int(self.file_tmp_in.readline())
            self.nit = self.ni
            self.r39 = np.zeros(self.ni, dtype=np.float64)
            self.telab = np.zeros(self.ni, dtype=np.float64)
            self.tilab = np.zeros(self.ni, dtype=np.float64)
            for i in range(self.ni):
                self.telab[i] = float(self.file_tmp_in.readline())
                self.tilab[i] = float(self.file_tmp_in.readline())
                self.tilab[i] /= 5.256E+11  # 1 Ma = 525600000000 minutes
                if self.telab[i] > 1373:
                    # go to 11
                    self.ni = i
                    break

            # 读取sig
            self.sig = np.zeros(self.ns, dtype=np.float64)
            self.xs = np.zeros(self.ns + 1, dtype=np.float64)
            self.ya = np.zeros(self.ns + 1, dtype=np.float64)
            for i in range(self.nit + 1):
                try:
                    self.sig[i] = float(self.file_sig_in.readline())
                    if self.sig[i] <= 0:
                        raise ValueError("Sigma less than 0")
                    self.xs[i + 1], self.ya[i + 1] = [float(j) for j in filter(lambda x: is_number(x),
                                                                               self.file_age_in.readline().split(' '))]
                    self.xs[i + 1] /= 100
                    if self.ya[i] < 0:
                        self.ya[i] = 0
                except ValueError:
                    print(f"{i = } error in reading sig file")
                continue

            self.file_tmp_in.close()
            self.file_age_in.close()
            self.file_sig_in.close()

        # 读取
        nemax = 0
        self.nst_arr = np.zeros(100, dtype=int)
        self.e_arr = np.zeros(100, dtype=np.float64)
        self.d0_arr = np.zeros([100, 20], dtype=np.float64)
        self.vc_arr = np.zeros([100, 20], dtype=np.float64)
        self.e = 0
        self.d0 = np.zeros(self.nd, dtype=np.float64)
        self.vc = np.zeros(self.nd, dtype=np.float64)
        kk = 0
        while True:
            try:
                self.nst_arr[kk] = int(self.file_ame_in.readline())  # sequence number
                # self.nst = int(self.file_ame_in.readline())  # sequence number
                for i in range(self.nst_arr[kk]):
                    self.e_arr[kk] = float(self.file_ame_in.readline())
                    self.d0_arr[kk, i] = 10 ** float(self.file_ame_in.readline()) / 4 * (24 * 3600 * 365e+6)
                    self.vc_arr[kk, i] = float(self.file_ame_in.readline())
                    # self.e = float(self.file_ame_in.readline())
                    # self.d0[i] = float(self.file_ame_in.readline())
                    # self.vc[i] = float(self.file_ame_in.readline())
                    # self.d0[i] = 10 ** self.d0[i] / 4 * (24 * 3600 * 365e+6)
                    nemax += 1
                self.atmp = self.file_ame_in.readline()
                self.atmp = self.file_ame_in.readline()
                self.atmp = self.file_ame_in.readline()
                kk += 1
            except ValueError:
                break
        self.kk = kk
        print(f"{self.kk = }")


        self.max_plateau_age = 10

        self.file_ame_in.close()

    def main(self):

        ###
        # initialize
        lista = np.zeros(self.nc, dtype=int)
        c0 = np.zeros(self.nc, dtype=np.float64)
        c = np.zeros(self.nc, dtype=np.float64)
        chq = np.zeros(self.nwcy, dtype=np.float64)
        nchini = 0
        tt = np.zeros([2, self.ntst + 1], dtype=np.float64)
        tt[0, 1] = self.max_plateau_age

        for kk in range(self.kk):

            stop_main = False

            print(f"New kk")
            print(f"{kk = }")

            mcyc = 0
            agein = tt[0, 1]
            idem = -1 * tt[0, 1]
            tt[1, 1] = 500
            tt[1, 2] = 300
            tt[0, 2] = tt[0, 1] / 2
            tt[1, 3] = 0
            tt[0, 3] = 0
            self.ncyc = 1
            chqmin = 1e20

            # calculation of lc
            self.lc = np.zeros(self.nn, dtype=int)
            nsq = 2
            nsum = 0
            m = -1
            for mi in range(self.nn):
                if nsum > 20:
                    nsum = 1
                    nsq *= 2
                m += nsq
                if m > 200:
                    nsum += 1
                self.lc[mi] = m

            self.func = self
            self.ran1 = Ran1Generator(idum=idem)

            self.r39 = self.r39[:self.ni + 1]
            self.telab = self.telab[:self.ni]
            self.tilab = self.tilab[:self.ni]
            self.lc = self.lc[:self.nn]

            # self.d0 = self.d0[:self.nst]
            # self.vc = self.vc[:self.nst]

            self.nst = self.nst_arr[kk]
            self.d0 = self.d0_arr[kk, :self.nst]
            self.vc = self.vc_arr[kk, :self.nst]
            self.e = self.e_arr[kk]

            print(f"{self.e = }")

            xmat = np.zeros([self.nd, self.ns + 1, self.nn], dtype=np.float64)

            # call lab
            self.r39, self.d0, self.e, self.vc, self.telab, self.tilab, self.lc, xmat, self.ni, self.nst, self.nn = \
                self.lab(self.r39, self.d0, self.e, self.vc, self.telab, self.tilab,
                         self.lc, xmat, self.ni, self.nst, self.nn)

            ys = np.zeros(self.ns + 2, dtype=np.float64)
            ne = 1
            self.r39 = np.pad(self.r39, (0, self.nit - self.ni), mode='constant', constant_values=0)
            self.wt = np.zeros(self.ni + 1, dtype=np.float64)
            for i in range(self.ni + 1):
                self.wt[i] = 1 / np.sqrt(abs(self.r39[i + 1] - self.r39[i])) * self.sig[i]

            # call agesamp
            # print(f"{self.ya = }")
            # print(f"{ys = }")
            # print(f"{self.r39 = }")
            # print(f"{self.xs = }")
            ys = self.agesamp(self.r39, ys, self.wt, self.nit, ne, self.ya, self.xs)
            # print(f"{ys = }")

            c = np.zeros(self.nc, dtype=np.float64)
            _np = 3
            a = 0

            # call chebft
            c = self.chebft(a, tt[0, 1], c, self.nc, self.slope, tt, _np)

            # print(f"{c = }")
            # print(f"{len(c) = }")

            for i in range(self.mfit):
                lista[i] = i
                c0[i] = c[i]

            while True:

                # call ranchist
                c, tt[1, 1] = self.ranchist(c, c0, self.mfit, idem, tt[1, 1])

                # print(f"after ranchist")
                # print(f"{c = }")
                # print(f"{len(c) = }")

                dch = 0
                alamda = -1

                chisq = 0
                nn1 = self.nn
                covar = np.zeros([self.nc, self.nc], dtype=np.float64)
                alpha = np.zeros([self.nc, self.nc], dtype=np.float64)

                # call mrqmin
                # print(f"{chisq = }")

                print(f"{self.ya = }")
                # print(f"{self.r39 = }")
                # print(f"{ys = }")
                # print(f"{self.wt = }")
                # print(f"{self.ni = }")
                # print(f"{c = }")
                # print(f"{self.nc = }")
                # print(f"{lista = }")
                # print(f"{self.mfit = }")
                # # print(f"{covar = }")
                # # print(f"{alpha = }")
                # print(f"{chisq = }")
                # print(f"{alamda = }")
                # # print(f"{tt = }")
                # # print(f"{xmat = }")
                # print(f"{self.lc = }")
                # print(f"{self.vc = }")
                # print(f"{self.d0 = }")
                # print(f"{self.e = }")
                # print(f"{self.nst = }")
                # print(f"{nn1 = }")



                self.r39, ys, self.wt, self.ni, c, self.nc, lista, self.mfit, covar, alpha, self.nc, chisq, alamda, tt, xmat, self.lc, self.vc, self.d0, self.e, self.nst, nn1 = \
                    self.func.mrqmin_agemon(self.r39, ys, self.wt, self.ni, c, self.nc, lista, self.mfit, covar,
                                            alpha, self.nc, chisq, alamda, tt, xmat, self.lc, self.vc, self.d0,
                                            self.e, self.nst, nn1)
                # print(f"{chisq = }")

                # print(f"{c = }")
                # print(f"{len(c) = }")

                k = 1
                itst = 0

                alam = alamda
                while True:

                    print(f"it #= {k}, {alamda = }, {chisq = }, ochisq = {self.ochisq}")

                    if dch > 0:
                        print(f"chi-squared = {self.ni * chisq}")

                    k += 1
                    ochisq = chisq

                    # print(f"{self.r39 = }")
                    # print(f"{ys = }")
                    # print(f"{self.wt = }")
                    # print(f"{self.ni = }")
                    # print(f"{c = }")
                    # print(f"{self.nc = }")
                    # print(f"{lista = }")
                    # print(f"{self.mfit = }")
                    # # print(f"{covar = }")
                    # # print(f"{alpha = }")
                    # print(f"{chisq = }")
                    # print(f"{alamda = }")
                    # # print(f"{tt = }")
                    # # print(f"{xmat = }")
                    # print(f"{self.lc = }")
                    # print(f"{self.vc = }")
                    # print(f"{self.d0 = }")
                    # print(f"{self.e = }")
                    # print(f"{self.nst = }")
                    # print(f"{nn1 = }")


                    # call mrqmin
                    self.r39, ys, self.wt, self.ni, c, self.nc, lista, self.mfit, covar, alpha, self.nc, chisq, alamda, tt, xmat, self.lc, self.vc, self.d0, self.e, self.nst, nn1 = \
                        self.func.mrqmin_agemon(self.r39, ys, self.wt, self.ni, c, self.nc, lista, self.mfit, covar,
                                                alpha, self.nc, chisq, alamda, tt, xmat, self.lc, self.vc, self.d0,
                                                self.e, self.nst, nn1)

                    dch = abs(ochisq - chisq)
                    cht = self.cht0 * chisq

                    if dch < cht and alamda < alam:
                        itst += 1
                        # print(f"{itst = }")

                    alam = alamda
                    if itst < 3:
                        continue
                    else:
                        break
                #
                # print(f"{ochisq = }")
                # print(f"{chisq = }")
                print(f"difference = {(ochisq - chisq) * self.ni}")

                chq[self.ncyc] = chisq
                aq = (self.ni - 2) / 2
                # q = gammq(aq, self.ni * chisq / 2)
                q = self.func.gammq(aq, self.ni * chisq / 2)

                print(f"chisq = {self.ni * chisq}, GOF = {q}")

                alamda = 0
                c40 = 1 - np.exp(-self.xlambd * tt[0, 1])

                # call zita
                xi = np.zeros([2 * self.nc + 1, self.nd, self.mxi], dtype=np.float64)

                c, xi = self.func.zita_agemon(
                    c, self.nc, lista, self.mfit, self.lc, xi, tt[0, 1],
                    self.d0, self.e, tt, self.nst, self.nn, self.perc, alamda)

                ymod = 0
                dyda = np.zeros(self.mfit, dtype=np.float64)
                for i in range(1, self.ni + 1):
                    # call age
                    ymod, dyda = self.func.age(
                        i, c, ymod, dyda, self.nc, lista, self.mfit,
                        self.vc, xmat, self.r39, xi, c40, self.nn,
                        self.nst, self.ni, self.perc, alamda)
                    # print(f"after age funcs {alamda = }")

                    continue

                # print(f"{nchini = }, {chisq = }")

                if nchini == 0:
                    chqmin = chisq
                nchini += 1

                print(f"new cycle: {nchini}")
                print(f"{self.ncyc = }, {nchini = }")

                # 1, 1
                # 2, 2
                # 3, 3
                # 4, 4
                # 5, 5

                # print(f"{chq = }")
                # print(f"{chqmin = }")

                self.file_output_mch = open(os.path.join(self.loc, f"{self.sname}_mch-out.dat"), "a+")
                self.file_output_mages = open(os.path.join(self.loc, f"{self.sname}_mages-out.dat"), "a+")
                if kk == 0 and nchini == 1:
                    self.file_output_agesd = open(os.path.join(self.loc, f"{self.sname}_ages-sd.samp"), "a+")

                if self.ncyc == self.nwcy or nchini >= self.nrun:
                    if self.ncyc == nchini:
                        for i in range(1, self.ncyc + 1):
                            if chq[i] < chqmin:
                                chqmin = chq[i]
                    for i in range(1, self.ncyc + 1):

                        kcyc = nchini - self.ncyc + i

                        print(f"{chq[i] = }, {chqmin = }")

                        if chq[i] < chqmin * 1.5:
                            mcyc += 1
                            n1 = 0

                            for j in range(self.nmaxo[i]):
                                line = f"{self.tto[i - 1, 0, j]}\t{self.tto[i - 1, 1, j]}"
                                self.file_output_mch.writelines(line + "\n")

                                continue

                            for j in range(self.ni):
                                line = f"{self.ageo[i - 1, 0, j]}\t{self.ageo[i - 1, 1, j]}"
                                self.file_output_mages.writelines(line + "\n")
                                line = f"{self.ageo[i - 1, 0, j + 1]}\t{self.ageo[i - 1, 1, j]}"
                                self.file_output_mages.writelines(line + "\n")

                            line = f"&  cycle # {kcyc}, chisq = {chq[i] * self.ni}, e = {self.e}"
                            self.file_output_mages.writelines(line + "\n")
                            line = f"&  cycle # {kcyc}, chisq = {chq[i] * self.ni}, e = {self.e}"
                            self.file_output_mch.writelines(line + "\n")
                            print(line)

                        continue

                    self.ncyc = 1
                else:
                    self.ncyc += 1

                self.file_output_mch.close()
                self.file_output_mages.close()
                self.file_output_agesd.close()

                # if nchini != self.nrun:
                #     # goto 34
                #     pass  # 被注释了

                print(f"{mcyc = }, {nchini = }")

                if mcyc < self.nrun and nchini < self.maxrun:
                    # nrun = 5; maxrun = 15
                    # goto 34
                    continue
                else:
                    nchini = 0
                    ne += 1
                    if ne > self.nemax:
                        stop_main = True
                        break  # goto 1001
                    break  # goto 1000

            if stop_main:
                break

        return self.ageo, self.tto

    def lab(self, r39, d0, e, vc, telab, tilab, lc, xmat, ni, nst, nn):
        #         r39, d0, e, vc, telab, tilab, lc, xmat, ni, nst, nn

        print(f"\n== Run lab ==\n")
        print(f"{r39 = }")
        print(f"{d0 = }")
        print(f"{e = }")
        print(f"{vc = }")
        print(f"{telab = }")
        print(f"{tilab = }")
        print(f"{lc = }")
        # print(f"{xmat = }")
        print(f"{ni = }")
        print(f"{nst = }")
        print(f"{nn = }")

        # 3d array: xmat
        # 1d array: lc, zita, r39, tilab, telab, d0, vc

        # lab()
        pi = 3.14159265359
        imp = 2
        b = 8
        ns = 200
        r = 1.987e-3
        nd = 10
        zita = np.zeros(ns + 1, np.float64)

        nsq = 2
        nsq1 = 1
        for i in range(nn):
            an2 = (lc[i] * pi) ** 2
            xmat[0, ni + 1, i] = b / an2

            an2 = an2

            if i >= 120:
                if (i - 120) % 20 == 0:
                    nsq *= 2
                    nsq2 = int(nsq / imp)
                for mi in range(1, nsq1):
                    an = ((lc[i] - mi * imp) * pi) ** 2
                    xmat[0, ni + 1, i] += b / an * (nsq1 - mi) / nsq1
                if i == nn - 1:
                    # go to 60
                    continue
                for mi in range(1, nsq2):
                    an = ((lc[i] + mi * imp) * pi) ** 2
                    xmat[0, ni + 1, i] += b / an * (nsq2 - mi) / nsq2
                nsq1 = nsq2

        for k in range(nst):
            for nt in range(1, ni + 1):
                if k == 0:
                    r39[nt] = 0
                zita[nt] = zita[nt - 1] + d0[k] * tilab[nt - 1] * np.exp(-e / (r * telab[nt - 1]))
                nsq = 2
                nsq1 = 1
                for j in range(nn):
                    an2 = (lc[j] * pi) ** 2
                    if an2 * zita[nt] > 60:
                        for jx in range(j, nn):  # 注意这里的索引
                            xmat[k, nt, jx] = xmat[0, ni + 1, jx]
                        # go to 72
                        break
                    else:
                        xmat[k, nt, j] = xmat[0, ni + 1, j] - b * np.exp(-an2 * zita[nt]) / an2

                    if j >= 120:
                        if (j - 120) % 20 == 0:
                            nsq *= 2
                            nsq2 = int(nsq / imp)
                        for mi in range(1, nsq1):
                            an = ((lc[j] - mi * imp) * pi) ** 2
                            xmat[k, nt, j] -= b * np.exp(-an * zita[nt]) / an * (nsq1 - mi) / nsq1
                        if j == nn - 1:
                            continue
                        for mi in range(1, nsq2):
                            an = ((lc[j] + mi * imp) * pi) ** 2
                            xmat[k, nt, j] -= b * np.exp(-an * zita[nt]) / an * (nsq2 - mi) / nsq2

                        # print(f"\n{j = }")
                        # print(f"{an  = }")
                        # print(f"{zita[nt]  = }")
                        # print(f"{nsq1  = }")
                        # print(f"{nsq2  = }")
                        # print(f"{imp  = }")
                        # print(f"{lc[j]  = }")
                        # print(f"{xmat[k, nt, j]  = }")
                        # iiii = 1
                        # print(f"{k = }, {nt = }, {j = }")
                        # print(f"{xmat[k, nt, j] - xmat[k, nt-1, j] = }")

                        nsq1 = nsq2

                # _ = np.square(np.array(range(1, 80000+1, imp)) * pi)
                # _ = np.where(zita[nt] * _ > 100, (b * vc[k]) / _, (b * vc[k]) / _ * (1 - np.exp(-zita[nt] * _)))
                # r39[nt] = np.sum(_) + r39[nt]

                for k1 in range(1, 80000 + 1, imp):
                    an2 = (k1 * pi) ** 2
                    if zita[nt] * an2 > 100:
                        ab = 0
                    else:
                        ab = np.exp(-zita[nt] * an2)

                    # print(f"{ab = }")
                    # print(f"{b = }")
                    # print(f"{an2 = }")
                    # print(f"{vc[k] = }")

                    r39[nt] += (b * vc[k]) / an2 * (1 - ab)

                # print(f"{r39[nt] = }")

                continue
            continue
        # end loop

        # print(f"\n== Return lab ==\n")
        # print(f"{r39 = }")
        # print(f"{d0 = }")
        # print(f"{e = }")
        # print(f"{vc = }")
        # print(f"{telab = }")
        # print(f"{tilab = }")
        # print(f"{lc = }")
        # # print(f"{xmat = }")
        # print(f"{ni = }")
        # print(f"{nst = }")
        # print(f"{nn = }")

        return r39, d0, e, vc, telab, tilab, lc, xmat, ni, nst, nn

    def agesamp(self, r39, ys, wt, ni, ne, ya, xs):

        # print(f"\n== Run agesamp ==\n")
        # print(f"{r39 = }")
        # # print(f"{wt = }")
        # # print(f"{self.sig = }")
        # print(f"{ys = }")
        # print(f"{ni = }")  # ni = 42 for 12h
        # print(f"{ya = }")
        # print(f"{xs = }")

        self.file_output_agesd = open(os.path.join(self.loc, f"{self.sname}_ages-sd.samp"), "a+")

        for j in range(1, ni + 1):
            if ne == 1:
                line = f"{xs[j - 1] * 100}    {ya[j] + self.sig[j - 1]}"
                self.file_output_agesd.writelines(line + "\n")
                line = f"{xs[j] * 100}    {ya[j] + self.sig[j - 1]}"
                self.file_output_agesd.writelines(line + "\n")
            # xs[j] /= 100
            if ya[j] < 0:
                ya[j] = 0

        if ne == 1:
            for k in range(1, ni):
                line = f"{xs[ni - k + 1] * 100}    {ya[ni - k + 1] - self.sig[ni - k]}"
                self.file_output_agesd.writelines(line + "\n")
                line = f"{xs[ni - k] * 100}    {ya[ni - k + 1] - self.sig[ni - k]}"
                self.file_output_agesd.writelines(line + "\n")
            line = f"{xs[0]}    {ya[1] + self.sig[0]}"
            self.file_output_agesd.writelines(line + "\n")

        self.file_output_agesd.close()

        ya[0] = ya[1]
        xs[ni + 1] = 1
        ys[ni + 1] = ys[ni]
        jold = 1
        for k in range(1, ni + 1):
            ys[k] = 0
            # print(f"{jold = }, {r39[k] = }")
            for j in range(jold, ni + 2):
                # print(f"{xs[j - 1] = }, {r39[k] = }, {xs[j] = }")
                if xs[j - 1] < r39[k] and xs[j] > r39[k]:
                    if jold == j:
                        ys[k] = ya[j]
                    else:
                        for jm in range(jold + 1, j):
                            ys[k] = ya[jm] * (xs[jm] - xs[jm - 1]) + ys[k]
                        ys[k] += ya[jold] * (xs[jold] - r39[k - 1]) + ya[j] * (r39[k] - xs[j - 1])
                        ys[k] /= (r39[k] - r39[k - 1])
                        jold = j
                    # go to 30
                    break
                # end if
            # print(f"{ys[k] = }")
            continue

        # print(f"\n== Return agesamp ==\n")
        # print(f"{ys = }")
        # print(f"{r39 = }")
        # print(f"{wt = }")
        # print(f"{ni = }")
        # print(f"{ne = }")
        # print(f"{ya = }")
        # print(f"{xs = }")

        return ys

    def chebft(self, a, b, c, n, func, tt, _np):

        # print(f"\n== Return chebft ==\n")
        # print(f"{a = }")
        # print(f"{b = }")
        # print(f"{c = }")
        # print(f"{n = }")
        # print(f"{tt = }")

        nmax = 100
        pi = 3.141592653589793
        f = np.zeros(nmax, dtype=np.float64)

        # c[n], f[namx], tt[2, 0:np]

        bma = 0.5 * (b - a)
        bpa = 0.5 * (b + a)

        for k in range(n):
            y = np.cos(pi * (k + 0.5) / n)
            f[k] = func(tt, _np, y * bma + bpa)

        fac = 2 / n
        for j in range(n):
            sum = 0
            for k in range(n):
                sum += f[k] * np.cos(pi * j * (k + 0.5) / n)
            c[j] = fac * sum

        # print(f"\n== Return chebft ==\n")
        # print(f"{c = }")

        return c

    def slope(self, a, n, x):
        a = a[:2, :n + 1]
        res = 0
        for j in range(2, n + 1):
            if a[0, j] < x and a[0, j - 1] > x:
                res = np.sqrt(abs((a[1, j - 1] - a[1, j]) / (a[0, j - 1] - a[0, j])))
                break

        return res

    def ranchist(self, c, c0, mc, idem, tini):
        # c, c0, mfit, idem, tt[1, 1]

        # print(f"\n== Run ranchist ==")
        # print(f"{c0 = }")
        # print(f"{tini = }")
        # fsum2 = 0

        # print(f"{mc = }")

        for i in range(mc):
            perc = 5 * self.ran1.ran1() * (0.6 - self.ran1.ran1())
            c[i] = c0[i] + perc
        tini = (0.5 - self.ran1.ran1()) * 200 + 400

        # print(f"\n== Return ranchist ==")
        # print(f"{c = }")
        # print(f"{tini = }")

        return c, tini

    def mrqmin_agemon(self, x, y, sig, ndata, a, ma, lista, mfit, covar, alpha, nca,
                      chisq, alamda, tt, xmat, lc, vc, d0, e, nst, nn):
        # def mrqmin(self,r39,ys,wt,ni,c,nc,lista,mfit,covar,alpha,nc,chisq,alamda,tt,xmat,lc,vc,d0,E,nst,nn1):
        # print(f"\n======================================")
        # print(f"Run mrqmin_agemon")
        # print(f"======================================")
        #
        # print(f"{x = }")
        # print(f"{y = }")
        # print(f"{sig = }")
        # print(f"{ndata = }")
        # print(f"{a = }")
        # print(f"{ma = }")
        # print(f"{lista = }")
        # print(f"{mfit = }")
        # # print(f"{covar = }")
        # # print(f"{alpha = }")
        # print(f"{nca = }")
        # print(f"{chisq = }")
        # print(f"{alamda = }")
        # print(f"{tt = }")
        # print(f"{xmat = }")

        # print(f"in mrqmin {alamda = }, {chisq = }, {self.ochisq = }")

        mmax = 100
        ntst = 1001
        nd = 10
        ns = 200
        covaux = np.zeros([mmax, mmax], dtype=np.float64)
        daux = np.zeros(mmax, dtype=np.float64)

        if alamda < 0:
            kk = mfit
            for j in range(ma):
                ihit = 0
                for k in range(mfit):
                    if lista[k] == j:
                        ihit += 1
                if ihit == 0:
                    lista[kk] = j
                    kk += 1
                elif ihit > 1:
                    pass
            if kk != ma:
                pass
            # call mrqcof
            chisq, alpha, self.beta = \
                self.mrqcof_agemon(x, y, sig, ndata, a, ma, lista, mfit, alpha,
                                   self.beta, nca, chisq, tt, xmat, lc, vc, d0, e, nst, nn, alamda)
            # print(f"xxxxxxxxxxxxxxxxxx {self.beta = }")
            alamda = 0.001
            self.ochisq = chisq
            for j in range(ma):
                self.atry[j] = a[j]
        # end if

        # print(f"in mrqmin 001 {chisq = }, {self.ochisq = }")

        for j in range(mfit):
            for k in range(mfit):
                covar[j, k] = alpha[j, k]
            covar[j, j] = alpha[j, j] * (1 + alamda)
            self.da[j] = self.beta[j]
        ng = 1
        # call gaussj(covar, mfit, nca, da, ng, 1)
        # print(f"call gaussj")
        # print(f"xxxxxxxxxx before gaussj {self.da[0] = }")
        # print(f"xxxxxxxxxx before gaussj {covar[0] = }")

        # with open("c:\\Users\\Young\\Desktop\\newdata.txt") as f:
        #     line = f.readline()
        #     _covar = [float(i) for i in line.split(",")]
        #     covar = np.array(_covar).reshape([100, 100])
        #     line = f.readline()
        #     _da = [float(i) for i in line.split(",")]
        #     self.da = np.array(_da)


        ng = self.gaussj(covar, mfit, self.da, ng)  ########### covar 这里跟 C++不对
        # print(f"xxxxxxxxxx after gaussj {self.da[0] = }")
        # print(f"xxxxxxxxxx before gaussj {covar[0] = }")
        # print(f"end gaussj")
        # print(f"{ng = }")
        if ng == -1:
            raise ValueError('Singular Matrix')
        if alamda == 0:
            # call covsrt(covar, nca, ma, lista, mfit)
            covar = self.covsrt(covar, ma, lista, mfit)
            return x, y, sig, ndata, a, ma, lista, mfit, covar, alpha, nca, chisq, alamda, tt, xmat, lc, vc, d0, e, nst, nn

        # print(f"xxxxxxxxxx before mrqcof {a[0] = }")
        # print(f"xxxxxxxxxx before mrqcof {self.da[0] = }")
        # print(f"xxxxxxxxxx before mrqcof {self.beta[0] = }")

        for j in range(mfit):
            if alamda >= 1e20:
                self.da[j] = 0
            # print(f"{a[int(lista[j])] = }, {self.da[j] = }")
            self.atry[int(lista[j])] = a[int(lista[j])] + self.da[j]

        # print(f"in mrqmin 002 {chisq = }, {self.ochisq = }")

        # call mrqcof(x,y,sig,ndata,atry,ma,lista,mfit,covar,da,nca,chisq,tt,xmat,lc,vc,d0,e,nst,nn,alamda)
        # print(f"xxxxxxxxxx before mrqcof {self.atry[0] = }")
        chisq, covar, self.da = \
            self.mrqcof_agemon(x, y, sig, ndata, self.atry, ma, lista, mfit, covar,
                               self.da, nca, chisq, tt, xmat, lc, vc, d0, e, nst, nn, alamda)
        # print(f"xxxxxxxxxx after mrqcof {self.atry[0] = }")

        # print(f"xxxxxxxxxx after mrqcof {self.atry = }")

        # print(f"in mrqmin 003 {chisq = }, {self.ochisq = }")

        # print(f"{self.ochisq = }")
        if chisq <= self.ochisq:
            for j in range(mfit):
                for k in range(mfit):
                    covaux[j, k] = covar[j, k]
                daux[j] = self.da[j]
            # call gaussj(covaux,mfit,nca,daux,ng,1)
            ng = self.gaussj(covaux, mfit, daux, ng)
            if ng == -1:
                alamda = 10 * alamda
                chisq = self.ochisq
                ng = 1
                return x, y, sig, ndata, a, ma, lista, mfit, covar, alpha, nca, chisq, alamda, tt, xmat, lc, vc, d0, e, nst, nn
            alamda = 0.1 * alamda
            self.ochisq = chisq
            for j in range(mfit):
                for k in range(mfit):
                    alpha[j, k] = covar[j, k]
                self.beta[j] = self.da[j]
                a[int(lista[j])] = self.atry[int(lista[j])]
        else:
            alamda = 10 * alamda
            chisq = self.ochisq
        # end if

        # print(f"\n======================================")
        # print(f"Return mrqmin_agemon")
        # print(f"======================================")
        #
        # print(f"{alamda = }")
        # print(f"{chisq = }")
        # print(f"{ng = }")
        # print(f"{covar = }")
        # print(f"{alpha = }")
        # print(f"{self.beta = }")

        return x, y, sig, ndata, a, ma, lista, mfit, covar, alpha, nca, chisq, alamda, tt, xmat, lc, vc, d0, e, nst, nn

    def mrqcof_agemon(self, x, y, sig, ndata, a, ma, lista, mfit, alpha,
                      beta, nalp, chisq, tt, xmat, lc, vc, d0, e, nst, nn, al):

        # print(f"\n======================================")
        # print(f"Run mrqcof")
        # print(f"======================================")
        #
        # print(f"{x = }")
        # print(f"{y = }")
        # print(f"{sig = }")
        # print(f"{ndata = }")
        # print(f"{a = }")
        # print(f"{ma = }")
        # print(f"{lista = }")
        # print(f"{mfit = }")
        # print(f"{alpha = }")
        # print(f"{beta = }")

        mmax = 100
        ntst = 1001
        perc = 0.01
        xlambd = 0.0005543
        nc = 100
        mxi = 500
        nd = 10
        ns = 200

        t0 = tt[0, 1]
        c40 = 1 - np.exp(-xlambd * t0)

        for j in range(mfit):
            for k in range(j + 1):
                alpha[j, k] = 0
            beta[j] = 0

        xi = np.zeros([2 * nc + 1, nd, mxi], dtype=np.float64)

        # print(f"before zita {tt[0] = }")
        # print(f"xxxxxxxxxx before zita {a[0] = }")
        a, xi = self.zita_agemon(a, ma, lista, mfit, lc, xi, t0, d0, e, tt, nst, nn, perc, al)
        # print(f"xxxxxxxxxx before zita {a[0] = }")
        # print(f"end zita")
        # print(f"after zita {tt[0] = }")

        if tt[1, ntst] == -1:
            tt[1, ntst] = 0
            chisq = chisq * 2
            return
        # end if
        chisq = 0
        for i in range(1, ndata + 1):
            ymod = 0
            dyda = np.zeros(mfit, dtype=np.float64)
            # ymod, dyda = call age(i,a,ymod,dyda,ma,lista,mfit,vc,xmat,x,xi,c40,nn,nst,ndata,perc,al)
            # print(f"in mrqcof_agemon funcs, {i = }, {al = }")
            ymod, dyda = self.age(i, a, ymod, dyda, ma, lista, mfit, vc, xmat, x, xi, c40, nn, nst, ndata, perc, al)
            # print(f"{ymod = }")
            sig2i = 1 / (sig[i - 1] * sig[i - 1])

            # print(f"{dyda = }")
            # print(f"{sig2i = }")    # 检查这里是不是对的 alpha输入是零，输出有误差，导致gaussj计算不对

            dy = y[i] - ymod
            for j in range(mfit):
                wt = dyda[lista[j]] * sig2i
                for k in range(j + 1):
                    alpha[j, k] = alpha[j, k] + wt * dyda[lista[k]]
                beta[j] = beta[j] + dy * wt
            # print(f"{dy = }")
            # print(f"{sig2i = }")
            chisq = chisq + dy * dy * sig2i
            # print(f"{i = }, {dy = }, {sig2i = }, {ymod = }, {y[i] = }")
            # print(f"mrqcof {chisq = }")
        for j in range(1, mfit):
            for k in range(j):
                alpha[k, j] = alpha[j, k]

        # print(f"\n======================================")
        # print(f"Return mrqcof")
        # print(f"======================================")
        #
        # print(f"{x = }")
        # print(f"{y = }")
        # print(f"{sig = }")
        # print(f"{ndata = }")
        # print(f"{a = }")
        # print(f"{ma = }")
        # print(f"{lista = }")
        # print(f"{mfit = }")
        # # print(f"{alpha = }")
        # print(f"{beta = }")

        return chisq, alpha, beta

    def zita_agemon(self, c, mc, lista, mfit, lc, xi, t0, d0, e, tt, nst, nn, perc, al):

        # print("\n== Run zita_agemon ==\n")
        # print(f"{len(c) = }")
        # print(f"{c = }")
        # print(f"{mc = }")
        # print(f"{lista = }")
        # print(f"{mfit = }")
        # print(f"{lc = }")
        # print(f"{xi = }")
        # print(f"{t0 = }")
        # print(f"{d0 = }")
        # print(f"{e = }")
        # print(f"{tt = }")
        # print(f"{nst = }")
        # print(f"{nn = }")
        # print(f"{perc = }")
        # print(f"{al = }")

        def chebev(a, b, c, m, x):
            # a,b 是定义函数的定义域
            # c 是切比雪夫多项式展开系数数组
            # m 是多项式阶数
            # x 是需要计算的点
            # 切比雪夫多项式（Chebyshev polynomials）求值
            # if (x - a) * (x - b) > 0:
            #     pass

            # print(f"{a = }, {b = }, {m = }, {x = }")
            # print(f"{c = }")

            d = 0
            dd = 0
            y = (2 * x - a - b) / (b - a)  # 将 x 映射到切比雪夫多项式的标准定义域 [-1, 1] 上
            y2 = 2 * y
            for j in range(m, 1, -1):
                sv = d
                d = y2 * d - dd + c[j - 1]
                dd = sv

            return y * d - dd + 0.5 * c[0]

        def sched(a, t0, c, m, tt, i):

            # print("\n== Run sched ==\n")
            # print(f"{a = }")
            # print(f"{t0 = }")
            # print(f"{c = }")
            # print(f"{m = }")
            # print(f"{tt = }")
            # print(f"{i = }")

            step = 4
            nt = 10000
            ntst = 1001
            tmax = 100
            i = 1
            slp = (chebev(a, t0, c, m, t0)) ** 2
            dt = t0 / nt
            sum = slp * dt / 2
            for j in range(1, nt + 1):
                xj = t0 - j * dt
                if j == nt:
                    xj = 0
                slp = (chebev(a, t0, c, m, xj)) ** 2
                sum += slp * dt / 2

                # print(f"{j = }, {sum = }")

                if sum >= step or xj == 0:
                    tt[1, i + 1] = tt[1, i] - sum
                    tt[0, i + 1] = xj
                    sum = 0

                    # print(f"{i = }, {tt[1, i + 1] = }, {tt[0, i + 1] = }, {j = }")

                    i += 1
                    if tt[1, i] <= tmax:
                        tt[1, i] = 0
                        tt[0, i] = 0
                        break
                sum += slp * dt / 2

            # step = 4
            # nt = 10000
            # ntst = 1001
            # tmax = 100
            # i = 1
            # slp = (chebev(a, t0, c, m, t0)) ** 2
            # dt = t0 / nt
            # _sum = slp * dt / 2
            #
            # j = np.linspace(1, nt, nt, dtype=int)
            # xj = t0 - j * dt
            # xj[nt] = 0
            # slp = (chebev(a, t0, c, m, xj)) ** 2
            # _sum = _sum + sum(slp * dt / 2)
            #
            # for j in range(1, nt + 1):
            #     xj = t0 - j * dt
            #     if j == nt:
            #         xj = 0
            #     slp = (chebev(a, t0, c, m, xj)) ** 2
            #     sum += slp * dt / 2
            #     if sum >= step or xj == 0:
            #         tt[1, i + 1] = tt[1, i] - sum
            #         tt[0, i + 1] = xj
            #         sum = 0
            #         print(f"{i = }, {tt[1, i + 1] = }, {tt[0, i + 1] = }, {j = }")
            #         i += 1
            #         if tt[1, i] <= tmax:
            #             tt[1, i] = 0
            #             tt[0, i] = 0
            #             break
            #     sum += slp * dt / 2

            # step = 4
            # nt = 10000
            # tmax = 100
            #
            # slp = chebev(a, t0, c, m, t0) ** 2
            # dt = t0 / nt
            # sum_arr = np.zeros(nt + 1)
            # xj_arr = t0 - np.arange(nt + 1) * dt
            # xj_arr[-1] = 0  # ensure the last element is exactly zero
            #
            # slp_arr = chebev(a, t0, c, m, xj_arr) ** 2
            # sum_arr[1:] = np.cumsum(slp_arr[:-1] + slp_arr[1:]) * dt / 2
            # sum_arr[0] = slp * dt / 2
            #
            # # Use boolean mask to find the steps
            # mask = sum_arr >= step
            # mask[-1] = True  # make sure the last element is considered
            #
            # indices = np.where(mask)[0]
            #
            # for idx in indices:
            #     if idx == 0:
            #         continue
            #     sum_val = sum_arr[idx]
            #     xj = xj_arr[idx]
            #     tt[1, i + 1] = tt[1, i] - sum_val
            #     tt[0, i + 1] = xj
            #     sum_arr[idx:] -= sum_val
            #     print(f"{i = }, {tt[1, i + 1] = }, {tt[0, i + 1] = }")
            #     i += 1
            #     if tt[1, i] <= tmax:
            #         tt[1, i] = 0
            #         tt[0, i] = 0
            #         break

            # print("\n== Return sched ==\n")
            # print(f"{i = }")

            return tt, i

        def sched2(a, t0, c, m, tt, i):
            nt = 10000
            tmax = 100
            i = 1
            slp = (chebev(a, t0, c, m, t0)) ** 2
            dt = t0 / nt
            sum = slp * dt / 2
            for j in range(1, nt + 1):
                xj = t0 - j * dt
                if j == nt:
                    xj = 0
                slp = (chebev(a, t0, c, m, xj)) ** 2
                sum += slp * dt / 2
                if xj == tt[0, i + 1]:
                    tt[1, i + 1] = tt[1, i] - sum
                    sum = 0
                    i += 1
                    if tt[1, i] <= tmax:
                        tt[1, i] = 0
                        tt[0, i] = 0
                        break
                sum += slp * dt / 2
            return tt, i

        # def geosec_new(imax,d0,e,tt,xi,nn,lc,nst,j1):
        #
        #     start_time = time.time()
        #
        #     # print("\n== Run geosec ==\n")
        #     # print(f"{imax = }")
        #     # print(f"{d0 = }")
        #     # print(f"{e = }")
        #     # print(f"{tt = }")
        #     # # print(f"{xi = }")
        #     # print(f"{nn = }")
        #     # print(f"{lc = }")
        #     # print(f"{nst = }")
        #     # print(f"{j1 = }")
        #
        #     xlambd = 5.543e-4
        #     r = 1.987e-3
        #     max = 1002
        #     pi = 3.14159265359
        #     nc = 100
        #
        #     d = np.zeros(max, dtype=np.float64)
        #     dzita = np.zeros(max, dtype=np.float64)
        #     nend = imax - 1
        #
        #     # print(f"{max = }")
        #     # print(f"{nend = }")
        #
        #     dzita[nend+1] = 0
        #
        #     # print(f"循环次数 = {nst * (int(nend) + nend + nn * nend)}")
        #
        #     avtemp = (tt[1, :-1] + tt[1, 1:]) / 2 + 273
        #     d = np.zeros(max, dtype=np.float64)
        #     d[1:] = np.where(e / r / avtemp > 80, np.exp(-e / r / avtemp), 0)
        #     d = d0.reshape(-1, 1) @ avtemp.reshape(1, -1)
        #
        #     xal = tt[0, 1:-1] - tt[0, 2:]
        #
        #     for k in range(nst):
        #
        #         # for j in range(int(nend)):
        #             # avtemp = (tt[1,j+2]+tt[1,j+1])/2 + 273
        #             # if e / r / avtemp > 80:
        #             #     d[j + 1] = 0
        #             #     # go to 10
        #             #     continue
        #             # d[j + 1] = d0[k] * np.exp(-e / r / avtemp)
        #
        #         # dzita[nend+1] = 0
        #
        #         for j in range(nend, 0, -1):
        #
        #             dzita[j] = dzita[j + 1] + abs(tt[0, j+1] - tt[0, j]) * d[k, j]
        #
        #         for mi in range(nn):
        #             xlogm = 2 * np.log(lc[mi] * pi)
        #             # sum = 0
        #
        #             uplus = (lc[mi] * pi) ** 2 * dzita[2:] + xlambd * (tt[0, 1] - tt[0, 2:])
        #
        #             al = (lc[mi] * pi) ** 2 * d[k, 1:] - xlambd
        #             #
        #             # print(uplus.shape)
        #             # print(xal.shape)
        #
        #             camal = np.where(abs(xal) > 30, 1, np.where(abs(xal) > 0.001, (1 - np.exp(-xal * al)) / al, xal * (1 - xal * al / 2 + xal ** 2 / 6)))
        #
        #             _sum = sum(d[k, 1:] * np.exp(-uplus) * camal)
        #
        #
        #             # for n in range(1, nend + 1):
        #             #     if d[n] == 0:
        #             #         # go to 40
        #             #         continue
        #             #     uplus = (lc[mi]*pi)**2*dzita[n+1]+xlambd*(tt[0,1]-tt[0,n+1])
        #             #     if uplus - xlogm > 25:
        #             #         # go to 40
        #             #         continue
        #             #     al = (lc[mi]*pi)**2*d[n]-xlambd
        #             #     xal = al * (tt[0, n] - tt[0, n + 1])
        #             #     if abs(xal) > 30:
        #             #         camal = 1 / al
        #             #     else:
        #             #         if abs(xal) > 0.001:
        #             #             camal = (1 - np.exp(-xal)) / al
        #             #         else:
        #             #             camal = (tt[0,n]-tt[0,n+1])*(1-xal/2+xal**2/6)
        #             #     sum += d[n]*np.exp(-uplus)*camal
        #             tzita = dzita[1] * (pi * lc[mi]) ** 2
        #             if tzita < 30:
        #                 xfact = np.exp(-tzita)
        #             else:
        #                 xfact = 0
        #             xi[j1, k, mi] = _sum * (pi * lc[mi]) ** 2 + xfact
        #         continue
        #
        #     print(f"geosec 耗时 ： {time.time() - start_time} 秒")
        #
        #     return imax,d0,e,tt,xi,nn,lc,nst,j1

        def geosec(imax, d0, e, tt, xi, nn, lc, nst, j1):

            # print("\n== Run geosec ==\n")
            # print(f"{imax = }")
            # print(f"{d0 = }")
            # print(f"{e = }")
            # print(f"{tt = }")
            # print(f"{xi = }")
            # print(f"{nn = }")
            # print(f"{lc = }")
            # print(f"{nst = }")
            # print(f"{j1 = }")

            # start_time = time.time()

            xlambd = 5.543e-4
            r = 1.987e-3
            max = 1002
            pi = 3.14159265359
            nc = 100

            d = np.zeros(max + 1, dtype=np.float64)
            dzita = np.zeros(max + 1, dtype=np.float64)
            nend = imax - 1

            dzita[nend + 1] = 0

            # print(f"循环次数 = {nst * (int(nend) + nend + nn * nend)}")

            for k in range(nst):

                for j in range(int(nend)):
                    avtemp = (tt[1, j + 2] + tt[1, j + 1]) / 2 + 273
                    if e / r / avtemp > 80:
                        d[j + 1] = 0
                        # go to 10
                        continue
                    d[j + 1] = d0[k] * np.exp(-e / r / avtemp)

                dzita[nend + 1] = 0

                for j in range(nend, 0, -1):
                    dzita[j] = dzita[j + 1] + abs(tt[0, j + 1] - tt[0, j]) * d[j]

                for mi in range(nn):
                    xlogm = 2 * np.log(lc[mi] * pi)
                    sum = 0
                    for n in range(1, nend + 1):
                        if d[n] == 0:
                            # go to 40
                            continue
                        uplus = (lc[mi] * pi) ** 2 * dzita[n + 1] + xlambd * (tt[0, 1] - tt[0, n + 1])
                        if uplus - xlogm > 25:
                            # go to 40
                            continue
                        al = (lc[mi] * pi) ** 2 * d[n] - xlambd
                        xal = al * (tt[0, n] - tt[0, n + 1])
                        if abs(xal) > 30:
                            camal = 1 / al
                        else:
                            if abs(xal) > 0.001:
                                camal = (1 - np.exp(-xal)) / al
                            else:
                                camal = (tt[0, n] - tt[0, n + 1]) * (1 - xal / 2 + xal ** 2 / 6)
                        sum += d[n] * np.exp(-uplus) * camal
                    tzita = dzita[1] * (pi * lc[mi]) ** 2
                    if tzita < 30:
                        xfact = np.exp(-tzita)
                    else:
                        xfact = 0
                    xi[j1, k, mi] = sum * (pi * lc[mi]) ** 2 + xfact
                    continue
                continue

            # print(f"geosec 耗时 ： {time.time() - start_time} 秒")

            # print("\n== Return geosec ==\n")
            # print(f"{imax = }")
            # print(f"{d0 = }")
            # print(f"{e = }")
            # print(f"{tt = }")
            # print(f"{xi = }")
            # print(f"{nn = }")
            # print(f"{lc = }")
            # print(f"{nst = }")
            # print(f"{j1 = }")

            return imax, d0, e, tt, xi, nn, lc, nst, j1

        start_time_1 = time.time()

        ntst = 1001
        a = 0
        nc = 100
        nwcy = 10
        ns = 200

        n = 0
        imax = 0

        # print(f"before sched {tt[0] = }")
        # imax = call sched(a, t0, c, mc, tt, imax)
        # print("before sched")
        tt, imax = sched(a, t0, c, mc, tt, imax)
        # print(f"after sched {tt[0] = }")
        # print(f"{xi = }")
        # call geosec(imax, d0, E, tt, xi, nn, lc, nst, n)
        # print("before geosec")
        imax, d0, e, tt, xi, nn, lc, nst, n = geosec(imax, d0, e, tt, xi, nn, lc, nst, n)

        if al <= 0:
            if al > 0:
                self.nmaxi[self.ncyc] = imax
            else:
                self.nmaxo[self.ncyc] = imax
            for j in range(imax):
                if al < 0:
                    self.tti[self.ncyc - 1, 0, j] = tt[0, j + 1]
                    self.tti[self.ncyc - 1, 1, j] = tt[1, j + 1]
                else:
                    self.tto[self.ncyc - 1, 0, j] = tt[0, j + 1]
                    self.tto[self.ncyc - 1, 1, j] = tt[1, j + 1]

        for k in range(mfit):
            csk = c[lista[k]]
            dc = perc * abs(c[lista[k]])
            for js in range(1, 3, 1):
                n += 1
                c[lista[k]] += (-1) ** js * dc
                # call ched2(a,t0,c,mc,tt,imax)
                # print("before sched")
                # print(f"before sched2 {tt[0] = }")
                tt, imax = sched2(a, t0, c, mc, tt, imax)
                # print(f"after sched2 {tt[0] = }")

                # call geosec(imax,d0,E,tt,xi,nn,lc,nst,n)
                # print("before geosec")
                imax, d0, e, tt, xi, nn, lc, nst, n = geosec(imax, d0, e, tt, xi, nn, lc, nst, n)
                c[lista[k]] = csk

        # print("\n== Return zita_agemon ==\n")
        # # print(f"{xi = }")
        # print(f"{c = }")

        print(f"zita 耗时 ： {time.time() - start_time_1} 秒")
        # print(f"{xi[0][0][0] = }")

        # print(f"{c = }")
        # print(f"{xi = }")
        # print(f"{tt = }")

        return c, xi

    def gaussj(self, a, n, b, m):
        # m = b.shape[1]

        nmax = 100
        ipiv = np.zeros(nmax, dtype=int)
        indxr = np.zeros(nmax, dtype=int)
        indxc = np.zeros(nmax, dtype=int)

        # print(f"\n======================================")
        # print(f"Run gaussj")
        # print(f"======================================")
        # print(f"{a = }")
        # print(f"{n = }")
        # print(f"{b = }")
        # print(f"{m = }")

        for j in range(n):
            ipiv[j] = 0

        for i in range(n):
            big = 0.0
            for j in range(n):
                if ipiv[j] != 1:
                    for k in range(n):
                        if ipiv[k] == 0:
                            if abs(a[j, k]) >= big:
                                big = abs(a[j, k])
                                irow = j
                                icol = k
                        elif ipiv[k] > 1:
                            m = -1
                            return m

            ipiv[icol] += 1
            if irow != icol:
                for l in range(n):
                    dum = a[irow, l]
                    a[irow, l] = a[icol, l]
                    a[icol, l] = dum

                for l in range(1):
                    # dum = b[v, irow]
                    # b[v, irow] = b[v, icol]
                    # b[v, icol] = dum
                    dum = b[irow]
                    b[irow] = b[icol]
                    b[icol] = dum

            indxr[i] = irow
            indxc[i] = icol
            if a[icol, icol] == 0:
                m = -1
                return m

            pivinv = 1 / a[icol, icol]

            a[icol, icol] = 1
            a[icol] *= pivinv
            b[icol] *= pivinv

            for ll in range(n):
                if ll != icol:
                    dum = a[ll, icol]
                    a[ll, icol] = 0
                    a[ll, :] -= a[icol, :] * dum
                    b[ll] -= b[icol] * dum

        for l in range(n - 1, -1, -1):
            if indxr[l] != indxc[l]:
                a[:, [indxr[l], indxc[l]]] = a[:, [indxc[l], indxr[l]]]

        # print(f"\n======================================")
        # print(f"Return gaussj")
        # print(f"======================================")
        # print(f"{a = }")
        # print(f"{n = }")
        # print(f"{b = }")
        # print(f"{m = }")

        return m

    def age(self, nt, c, y, dyda, mc, lista, mfit, vc, xmat, r39, xi, c40, nn, nst, ndata, perc, al):

        # print(f"\n== Run age ==\n")
        # print(f"{c40 = }")
        # print(f"{r39 = }")
        # print(f"{nt = }")
        # print(f"{nst = }")
        # print(f"{nn = }")
        # print(f"{vc = }")
        # print(f"{xi = }")
        # print(f"{xmat = }")

        xlambd = 0.0005543
        nc = 100
        nd = 10
        ns = 200
        nwcy = 10
        ntst = 1001

        dya = 0

        c39wd = 1 - c40
        s1 = 0

        # print(f"{xmat[0, 1, 0] - xmat[0, 0, 0] = }")
        # print(f"{xmat[0, 2, 0] - xmat[0, 1, 0] = }")
        # print(f"{xmat[0, 3, 0] - xmat[0, 2, 0] = }")
        # print(f"{xmat[0, 4, 0] - xmat[0, 3, 0] = }")
        # print(f"{xi[0][0][0] = }")
        for k in range(nst):
            for m in range(nn):
                s1 += vc[k] * xi[0, k, m] * (xmat[k, nt, m] - xmat[k, nt - 1, m])

            #     if m == 300 and nt == 2:
            #         print(f"{vc[k] = }, {xi[0, k, m] = }, {xmat[k, nt, m] = }, {xmat[k, nt - 1, m] = }")
            #         y = y
            # if nt == 2:
            #     print(f"{vc[k] = }, {xi[0, k, m] = }, {xmat[k, nt, m] = }, {xmat[k, nt - 1, m] = }")
            #     y = y

        # print(f"{nt = }, {s1 = }")

        dr39 = r39[nt] - r39[nt - 1]
        dr40 = dr39 * (c40 - 1) + s1

        y = 0
        if dr40 / dr39 > 0:
            y = np.log(1 + dr40 / dr39 / c39wd) / xlambd
            dya = 1 / (dr39 * c39wd + dr40) / xlambd

        # print(f"{dr40 = }, {dr39 = }, {c39wd = }")

        if nt == 2:
            nt = nt
        if al < 0:
            self.agei[self.ncyc - 1, 0, nt] = r39[nt] * 100
            self.agei[self.ncyc - 1, 1, nt - 1] = y
        elif al == 0:
            self.ageo[self.ncyc - 1, 0, nt] = r39[nt] * 100
            self.ageo[self.ncyc - 1, 1, nt - 1] = y

        # print(f"{self.ageo[self.ncyc - 1, 1, nt - 1] = }")

        for ls in range(1, mfit + 1):
            l = ls * 2 - 1
            dc = perc * abs(c[lista[ls - 1]])
            s1 = 0
            s1_list = []
            for k in range(nst):
                for m in range(nn):
                    dxi = (xi[l + 1, k, m] - xi[l, k, m]) / (2 * dc)
                    s1 += vc[k] * (xmat[k, nt, m] - xmat[k, nt - 1, m]) * dxi
                    s1_list.append(vc[k] * (xmat[k, nt, m] - xmat[k, nt - 1, m]) * dxi)
                    # print(f"{vc[k] = }")
                    # print(f"{xmat[k, nt, m] = }")
                    # print(f"{xmat[k, nt - 1, m] = }")
                    # print(f"{dxi = }")
                    # print(f"{xi[l + 1, k, m] = }")
                    # print(f"{xi[l, k, m] = }")
                    # print(f"{dc = }")

            # print(f"{s1 = }")
            # print(f"{kahan_sum(s1_list) = }")
            # print(f"{dya = }")

            dyda[lista[ls - 1]] = s1 * dya

        # print(f"\n== Return age ==\n")
        # print(f"{s1 = }")
        # print(f"{dr39 = }")
        # print(f"{dr40 = }")
        # # print(f"{y = }")
        # # print(f"{dyda = }")

        return y, dyda

    def covsrt(self, covar, ma, lista, mfit):
        # covar is expected to be a numpy array of shape (ncvm, ncvm)
        # lista is expected to be a numpy array of shape (mfit,)

        # Step 1: Zero out the upper triangle
        for j in range(ma - 1):
            for i in range(j + 1, ma):
                covar[i, j] = 0.0

        # Step 2: Reorganize the covariance matrix
        for i in range(mfit - 1):
            for j in range(i + 1, mfit):
                if lista[j] > lista[i]:
                    covar[int(lista[j]), int(lista[i])] = covar[i, j]
                else:
                    covar[int(lista[i]), int(lista[j])] = covar[i, j]

        # Step 3: Swap and reset diagonal elements
        swap = covar[0, 0]
        for j in range(ma):
            covar[0, j] = covar[j, j]
            covar[j, j] = 0.0

        covar[int(lista[0]), int(lista[0])] = swap

        for j in range(1, mfit):
            covar[int(lista[j]), int(lista[j])] = covar[0, j]

        # Step 4: Symmetrize the covariance matrix
        for j in range(1, ma):
            for i in range(j):
                covar[i, j] = covar[j, i]

        return covar

    def gammq(self, a, x):
        if x < 0 or a <= 0:
            raise ValueError("ERROR(GAMMQ): x < 0 or a <= 0")

        if x < a + 1:
            gamser, gln = self.gser(a, x)
            return 1.0 - gamser
        else:
            gammcf, gln = self.gcf(a, x)
            return gammcf

    def gser(self, a, x, itmax=100, eps=3e-7):
        gln = self.gammln(a)
        if x <= 0:
            if x < 0:
                raise ValueError("ERROR(GSER): x < 0")
            return 0.0, gln

        ap = a
        sum_ = 1.0 / a
        delta = sum_
        for n in range(1, itmax + 1):
            ap += 1
            delta *= x / ap
            sum_ += delta
            if abs(delta) < abs(sum_) * eps:
                break
        else:
            raise RuntimeError("ERROR(GSER): a too large, itmax too small")

        gamser = sum_ * np.exp(-x + a * np.log(x) - gln)
        return gamser, gln

    def gcf(self, a, x, itmax=100, eps=3e-7):
        gln = self.gammln(a)
        gold = 0.0
        a0 = 1.0
        a1 = x
        b0 = 0.0
        b1 = 1.0
        fac = 1.0
        for n in range(1, itmax + 1):
            an = float(n)
            ana = an - a
            a0 = (a1 + a0 * ana) * fac
            b0 = (b1 + b0 * ana) * fac
            anf = an * fac
            a1 = x * a0 + anf * a1
            b1 = x * b0 + anf * b1
            if a1 != 0:
                fac = 1.0 / a1
                g = b1 * fac
                if abs((g - gold) / g) < eps:
                    return g * np.exp(-x + a * np.log(x) - gln), gln
                gold = g
        else:
            raise RuntimeError("ERROR(GCF): a too large, itmax too small")

    def gammln(self, xx):
        cof = np.array([76.18009173, -86.50532033, 24.01409822,
                        -1.231739516, 0.00120858003, -0.00000536382])
        stp = 2.50662827465
        half = 0.5
        one = 1.0
        fpf = 5.5

        x = xx - one
        tmp = x + fpf
        tmp = (x + half) * np.log(tmp) - tmp
        ser = one
        for j in range(6):
            x += one
            ser += cof[j] / x

        return tmp + np.log(stp * ser)


class DiffDraw(DiffSample):
    def __init__(self, **kwargs):

        self.sname = ""
        self.loc = "D:\\PythonProjects\\ararpy_package\\ararpy\\examples\\20240710_24FY51a"

        super().__init__(**kwargs)

        self.file_mages_in = open(os.path.join(self.loc, f"{self.sname}_mages-out.dat"), "r")
        self.file_mch_in = open(os.path.join(self.loc, f"{self.sname}_mch-out.dat"), "r")
        self.file_agesd_in = open(os.path.join(self.loc, f"{self.sname}_ages-sd.samp"), "r")

        ns = 100
        k = 0


        read_from_ins = kwargs.get('read_from_ins', False)

        # 读取sig
        self.f = np.zeros(ns, dtype=np.float64)
        self.age = np.zeros(ns, dtype=np.float64)
        for i in range(ns):
            try:
                self.f[i], self.age[i] = [float(j) for j in filter(lambda x: is_number(x),
                                                                   [m for k in self.file_agesd_in.readline().split('\t')
                                                                    for m in str(k).split(' ')])]
                k += 1
            except ValueError:
                pass
            continue

        # print(f"{self.f = }")
        # print(f"{self.age = }")

        if read_from_ins:

            self.file_tmp_in = open(os.path.join(self.loc, f"{self.sname}_tmp.in"), "r")
            self.file_fj_in = open(os.path.join(self.loc, f"{self.sname}_fj.in"), "r")
            self.file_a39_in = open(os.path.join(self.loc, f"{self.sname}_a39.in"), "r")
            self.file_age_in = open(os.path.join(self.loc, f"{self.sname}_age.in"), "r")
            self.file_sig_in = open(os.path.join(self.loc, f"{self.sname}_sig.in"), "r")

            self.ni = int(self.file_tmp_in.readline())  # sequence number

            self.f = np.zeros(self.ni, dtype=np.float64)
            self.age = np.zeros(self.ni, dtype=np.float64)
            self.sage = np.zeros(self.ni, dtype=np.float64)
            self.a39 = np.zeros(self.ni, dtype=np.float64)
            self.sig39 = np.zeros(self.ni, dtype=np.float64)
            self.telab = np.zeros(self.ni, dtype=np.float64)
            self.tilab = np.zeros(self.ni, dtype=np.float64)

            for i in range(self.ni):
                try:
                    f, age = [float(j) for j in filter(lambda x: is_number(x),
                                                       [m for k in self.file_age_in.readline().split('\t') for m in
                                                        str(k).split(' ')])]
                    sage = float(self.file_sig_in.readline())  # age error
                    te = float(self.file_tmp_in.readline())  # heating temperature in Kelvin
                    ti = float(self.file_tmp_in.readline()) * 60  # heating time in second.
                    v, sv = [float(j) for j in filter(lambda x: is_number(x),
                                                      [m for k in self.file_a39_in.readline().split('\t') for m in
                                                       str(k).split(' ')])]
                except ValueError as e:
                    continue
                else:
                    self.f[i], self.age[i], self.sage[i] = f, age, sage
                    self.telab[i] = te
                    self.tilab[i] = ti
                    self.a39[i], self.sig39[i] = float(v), float(sv)

        self.mf = np.zeros([100, 1000], dtype=np.float64)
        self.mage = np.zeros([100, 1000], dtype=np.float64)
        self.mcte = np.zeros([100, 1000], dtype=np.float64)
        self.mcage = np.zeros([100, 1000], dtype=np.float64)

        self.mcyc = 0
        max_count = 0
        for cyc in range(100):
            count = 0
            for j in range(1000):
                try:
                    line = self.file_mages_in.readline().rstrip("\n")
                    # print(list(filter(lambda x: is_number(x), [m for k in self.file_mages_in.readline().split('\t') for m in str(k).split(' ')])))
                    f, age = [float(l) for l in
                              filter(lambda x: is_number(x), [m for k in line.split('\t') for m in str(k).split(' ')])]
                except ValueError as e:
                    break
                else:
                    self.mf[cyc, j], self.mage[cyc, j] = f, age
                    count += 1
            max_count = count if count > max_count else max_count
            if line == "":
                break
            self.mcyc += 1

        self.mf = self.mf[:self.mcyc, :max_count]
        self.mage = self.mage[:self.mcyc, :max_count]

        self.count = np.zeros(self.mcyc, dtype=int)
        for cyc in range(self.mcyc):
            for j in range(1000):
                try:
                    cage, cte = [float(l) for l in filter(lambda x: is_number(x),
                                                          [m for k in self.file_mch_in.readline().split('\t') for m in
                                                           str(k).split(' ')])]
                except ValueError as e:
                    # print(e)
                    break
                else:
                    self.mcte[cyc, j], self.mcage[cyc, j] = cte, cage
                    self.count[cyc] += 1

                # 每一组count不一样 下面的语句会裁剪
        # self.mcte = self.mcte[:self.mch, :self.mcyc, :count]
        # self.mcage = self.mcage[:self.mch, :self.mcyc, :count]

        # self.max_age = 75
        # self.min_age = 30
        # self.age_step = self.max_age - self.min_age

        # print(f"{self.ni = }")
        # print(f"{self.f = }")
        # print(f"{self.age = }")
        # print(f"{self.a39 = }")
        # print(f"{self.sig39 = }")
        # print(f"{self.telab = }")
        # print(f"{self.tilab = }")
        # print(f"{self.mf = }")
        # print(f"{self.mage = }")
        # print(f"{self.mcte = }")
        # print(f"{self.mcage = }")

    def get_plot_data(self):

        k1 = [x, y1, y2] = ap.calc.spectra.get_data(self.age, self.sage, [i * 100 for i in self.f], cumulative=True)
        k2 = []
        k3 = []
        for cyc in range(self.mcyc):
            x, y1, y2 = ap.calc.spectra.get_data(
                self.mage[cyc, :], np.zeros(self.mage[cyc, :].size), self.mf[cyc, :], cumulative=True)
            k2.append([x, y1, y2])
            k3.append([self.mcage[cyc, :], self.mcte[cyc, :]])

        # confidence
        (_b, _c) = self.mcage.shape
        k4 = [x_conf, y1_conf, y2_conf, y3_conf, y4_conf] = conf(
            self.mcage.reshape([_b, _c]), self.mcte.reshape([_b, _c]),
            count=self.count.flatten(), using_normal=True)

        return k1, k2, k3, k4

    def main(self):

        data = self.get_plot_data()
        # print(f"{self.mcyc = }")
        fig, [axs, axs2] = plt.subplots(2, 1)
        fig.set_size_inches(w=6, h=9)

        axs.set_title(f'Age spectra')
        axs.set_ylabel(f'Apparent age (Ma)')
        axs.set_xlabel(f'Cumulative 39Ar%')
        axs.set_xlim(0, 100)
        axs.set_ylim(0, 80)

        axs.plot(data[0][0], data[0][2], c='blue')
        axs.plot(data[0][0], data[0][1], c='blue')

        for cyc in range(self.mcyc):
            # x, y1, y2 = ap.calc.spectra.get_data(self.mage[cyc, :], np.zeros(self.mage[cyc, :].size), self.mf[cyc, :],
            #                                      cumulative=True)
            axs.plot(data[1][cyc][0], data[1][cyc][2], c='red')
            axs.plot(data[1][cyc][0], data[1][cyc][1], c='red')

        axs.legend()
        # axs.text(0, 0, f'{self.sname}')

        axs2.set_title(f'Cooling histories')
        axs2.set_ylabel(f'Temperature')
        axs2.set_xlabel(f'Age (Ma)')
        # axs2.set_xlim(30, 75)
        # axs2.set_ylim(0, 500)
        for cyc in range(self.mcyc):
            # axs2.plot(self.mcage[cyc, :], self.mcte[cyc, :], c='grey')
            axs2.plot(data[2][cyc][0], data[2][cyc][1], c='grey')

        # print(f"{self.mcage = }")

        # (_b, _c) = self.mcage.shape
        # x_conf, y1_conf, y2_conf, y3_conf, y4_conf = conf(
        #     self.mcage.reshape([_b, _c]), self.mcte.reshape([_b, _c]),
        #     count=self.count.flatten(), using_normal=True)
        x_conf, y1_conf, y2_conf, y3_conf, y4_conf = data[3]

        self.file_confmed_out = open(os.path.join(self.loc, f"{self.sname}_confmed.dat"), "w")
        for i in range(len(x_conf)):
            line = f"{x_conf[i]}    {y1_conf[i]}    {y2_conf[i]}    {y3_conf[i]}    {y4_conf[i]}"
            self.file_confmed_out.writelines(line + "\n")
        self.file_confmed_out.close()

        axs2.plot(x_conf, y1_conf, c='red')
        axs2.plot(x_conf, y2_conf, c='red')
        axs2.plot(x_conf, y3_conf, c='red')
        axs2.plot(x_conf, y4_conf, c='red')

        fig.tight_layout()
        plt.show()


class HeatingSequence:
    def __init__(self, SP, ST, ET, LB, LMin, LMax, LMean, LSD, UMin, UMax, UMean, USD,
                 x0, x1, x2, x3, x4, x5, x6, r2, Rise, Increment, MaxTime):
        self.SP, self.ST, self.ET, self.LB = SP, ST, ET, LB
        self.LMin, self.LMax, self.LMean, self.LSD = LMin, LMax, LMean, LSD
        self.UMin, self.UMax, self.UMean, self.USD = UMin, UMax, UMean, USD
        self.x0, self.x1, self.x2, self.x3, self.x4, self.x5, self.x6, self.r2 = x0, x1, x2, x3, x4, x5, x6, r2
        self.Rise, self.Increment, self.MaxTime = Rise, Increment, MaxTime

        self.x = [self.x0, self.x1, self.x2, self.x3, self.x4, self.x5, self.x6]


class InsideTemperatureCalibration:
    def __init__(self):

        self.loc = r'D:\DjangoProjects\webarar\static\settings'
        self.temp_regression_res = self.calculate_temp_conf()

    def get_seq(self, degree: int, increment=None, r2=0.5, minTime=0):

        if degree == 600 and increment is not None:
            increment = 500

        if increment is None:
            locs = np.where(
                [str(i.SP) == str(degree) and float(i.r2) >= float(r2) and float(i.MaxTime) >= float(minTime) for i in
                 self.sequences])
        else:
            locs = np.where([str(i.SP) == str(degree) and float(i.r2) >= float(r2) and float(i.MaxTime) >= float(
                minTime) and str(i.Increment) == str(increment) for i in self.sequences])

        return self.sequences[locs]

    def plot(self):

        path = r"/static/settings/Oven_log_regression_results.txt"

        file_in = open(path, "r")
        sequences = np.empty(10000, dtype=HeatingSequence)
        i = 0
        while True:
            line = file_in.readline().rstrip("\n")
            if line == "":
                break
            if line.startswith("SP"):
                continue
            values = line.split(",")
            sequences[i] = HeatingSequence(*values)
            i += 1

        file_in.close()

        sequences = sequences[:i]
        locs = np.where([i.Rise == "True" and int(i.Increment) >= 0 for i in sequences])
        self.sequences = sequences[locs]

        degrees = [600, 650, 700, 750, 800, 850, 900, 950, 1000,
                   1050, 1100, 1150, 1200, 1250, 1300, 1350, 1400, 1450, 1500]

        fig, axs = plt.subplots(4, 5)
        fig.set_size_inches(w=12, h=10)

        file_out = open(os.path.join(self.loc, f"conf_temperature_out.txt"), "w")
        file2_out = open(os.path.join(self.loc, f"conf_temperature_regression_out.txt"), "w")

        for index, ax in enumerate(axs.flatten()):

            if index >= len(degrees):
                break

            x_list = []
            y_list = []

            for seq in self.get_seq(degree=degrees[index], increment=50):
                x = np.linspace(0, int(seq.MaxTime), num=100)
                x_ = np.array([x ** 0, x ** 1, x ** 2, x ** 3, x ** 4, x ** 5, x ** 6]).transpose()

                y = np.sum(np.array(seq.x).astype(np.float64) * x_, axis=1)
                ax.plot(x, y, c='grey', alpha=0.5)
                ax.set_title(f'{degrees[index]} °C')

                x_list.append(x)
                y_list.append(y)

            # 拟合最优曲线

            # 参考 ：
            # https://www.zhihu.com/question/346773540/answer/2033802234
            # https://blog.csdn.net/weixin_46713695/article/details/126644568

            try:
                x_conf, y1_conf, y2_conf, y3_conf, y4_conf = conf(x_list, y_list, num=100, using_binom=True)
            except (ValueError, IndexError) as e:
                pass
            else:
                ax.plot(x_conf, y1_conf, c='red')
                ax.plot(x_conf, y2_conf, c='red')
                ax.plot(x_conf, y3_conf, c='red')
                ax.plot(x_conf, y4_conf, c='red')

                degree = 6
                x_conf = np.array(x_conf)

                file_out.writelines(f"{seq.SP = }, {seq.MaxTime = }, conf MaxTime = {max(x_conf)} \n")
                file2_out.writelines(f"SP = {seq.SP}, MaxTime = {max(x_conf)} \n")

                beta = ap.calc.regression.polynomial(y1_conf, x_conf, degree=degree)[5]
                ax.plot(x_conf, np.sum(beta * np.array([x_conf ** i for i in range(degree + 1)]).transpose(), axis=1),
                        c='blue')
                file_out.writelines("BetaY1\t" + "\t".join([str(i) for i in beta]) + "\n")
                file2_out.writelines("\t".join([str(i) for i in beta]) + "\n")

                beta = ap.calc.regression.polynomial(y2_conf, x_conf, degree=degree)[5]
                ax.plot(x_conf, np.sum(beta * np.array([x_conf ** i for i in range(degree + 1)]).transpose(), axis=1),
                        c='blue')
                file_out.writelines("BetaY2\t" + "\t".join([str(i) for i in beta]) + "\n")
                file2_out.writelines("\t".join([str(i) for i in beta]) + "\n")

                beta = ap.calc.regression.polynomial(y3_conf, x_conf, degree=degree)[5]
                ax.plot(x_conf, np.sum(beta * np.array([x_conf ** i for i in range(degree + 1)]).transpose(), axis=1),
                        c='blue')
                file_out.writelines("BetaY3\t" + "\t".join([str(i) for i in beta]) + "\n")
                file2_out.writelines("\t".join([str(i) for i in beta]) + "\n")

                beta = ap.calc.regression.polynomial(y4_conf, x_conf, degree=degree)[5]
                ax.plot(x_conf, np.sum(beta * np.array([x_conf ** i for i in range(degree + 1)]).transpose(), axis=1),
                        c='blue')
                file_out.writelines("BetaY4\t" + "\t".join([str(i) for i in beta]) + "\n")
                file2_out.writelines("\t".join([str(i) for i in beta]) + "\n")

                for i in range(len(x_conf)):
                    line = f"{x_conf[i]}\t{y1_conf[i]}\t{y2_conf[i]}\t{y3_conf[i]}\t{y4_conf[i]}"
                    file_out.writelines(line + "\n")

        file_out.close()
        file2_out.close()

        fig.tight_layout()
        plt.show()

    def plot_confidence(self):

        fig, ax = plt.subplots()
        fig.set_size_inches(w=12, h=10)

        file_in = open(os.path.join(self.loc, f"conf_temperature_out.txt"), "r")

        x_start = 0
        k = 0
        conf_x_max = 0

        while True:
            try:
                line = file_in.readline()

                if line.startswith("Beta"):
                    beta = [float(j) for j in
                            filter(lambda x: is_number(x), [m for k in line.split('\t') for m in str(k).split(' ')])]
                    k += 1

                if "conf MaxTime" in line:
                    conf_x_max = float(line.split('conf MaxTime = ')[-1])

                if 0 < k <= 2:
                    x = np.linspace(start=0, stop=conf_x_max, num=100)

                    _x = np.array([x ** 0, x ** 1, x ** 2, x ** 3, x ** 4, x ** 5, x ** 6]).transpose()
                    y = np.sum(beta * _x, axis=1)

                    ax.plot(x + x_start, y, c='blue')

                elif k == 4:
                    k = 0
                    x_start += conf_x_max

                if line == "":
                    break

            except Exception as e:
                print(e)
                break

        file_in.close()

        fig.tight_layout()
        plt.show()

    def plot_libano_log(self, libano_path: str):

        libano_log = open(libano_path, "r")
        log_time = []
        log_sp = []
        log_ap = []
        conf_ap1 = []
        conf_ap2 = []

        n = 0
        while True:
            line = libano_log.readline().rstrip("\n")
            if line == "":
                break
            k = line.split(";")
            log_time.append(dt.strptime(k[0], "%Y-%m-%dT%H:%M:%S%z").timestamp())
            log_sp.append(int(k[1]))
            log_ap.append(int(k[2]))
        # set time starts with zero
        log_time = [i - log_time[0] for i in log_time]
        libano_log.close()

        start_sp = -999
        start_time = 0
        for index, sp in enumerate(log_sp):
            if sp != start_sp:
                start_time = log_time[index]
            start_sp = sp
            try:
                ap1, ap2 = self.get_calibrated_temp(log_time[index] - start_time, sp)
            except (KeyError, ValueError):
                ap1, ap2 = 0, 0
            conf_ap1.append(ap1)
            conf_ap2.append(ap2)

        fig, ax = plt.subplots()
        fig.set_size_inches(w=12, h=10)
        ax.plot(log_time, log_sp, c='green')
        ax.plot(log_time, log_ap, c='blue')
        ax.plot(log_time, conf_ap1, c='red')
        ax.plot(log_time, conf_ap2, c='red')
        fig.tight_layout()
        plt.show()

    def calculate_temp_conf(self):

        file_in = open(os.path.join(self.loc, f"conf_temperature_regression_out.txt"), "r")
        k = 0
        conf_x_max = 0

        funcs = {}

        while True:

            line = file_in.readline().rstrip("\n")
            if line == "":
                break

            if line.startswith("SP"):
                pattern = r"SP = (\d+), MaxTime = (\d+\.\d+)"
                _ = re.search(pattern, line)
                conf_sp = float(_.groups()[0])
                conf_x_max = float(_.groups()[1])
                funcs[int(conf_sp)] = {"max_x": conf_x_max}
                k = 0
                pass
            else:
                beta = [float(j) for j in
                        filter(lambda x: is_number(x), [m for k in line.split('\t') for m in str(k).split(' ')])]
                k += 1

            if k == 1:
                funcs[int(conf_sp)].update({1: beta})
            if k == 2:
                funcs[int(conf_sp)].update({2: beta})
            if k == 4:
                k = 0

        file_in.close()

        return funcs

    def get_calibrated_temp(self, time, sp):
        funcs = self.temp_regression_res
        f1 = lambda x: sum(
            np.array(funcs[int(sp)][1]) * np.array([x ** 0, x ** 1, x ** 2, x ** 3, x ** 4, x ** 5, x ** 6]))
        f2 = lambda x: sum(
            np.array(funcs[int(sp)][2]) * np.array([x ** 0, x ** 1, x ** 2, x ** 3, x ** 4, x ** 5, x ** 6]))
        max_x = funcs[int(sp)]['max_x']
        ap1, ap2 = f1(time) if 0 <= time <= max_x else f1(max_x) if time > max_x else f1(0), f2(
            time) if 0 <= time <= max_x else f2(max_x) if time > max_x else f2(0)
        return ap1, ap2


class SmpTemperatureCalibration:
    def __init__(self, arr_path="", helix_log_path="", libano_log_path=None,
                 name="smp_example", loc=r'D:\DjangoProjects\webarar\static\settings'):

        self.name = name
        self.smp = ap.from_arr(file_path=arr_path)
        if isinstance(self.smp, Sample):
            self.name = self.smp.name()

        self.loc = loc

        self.helix_log_path = []
        if isinstance(helix_log_path, str):
            self.helix_log_path = [helix_log_path]
        elif isinstance(helix_log_path, list):
            self.helix_log_path = helix_log_path
        self.helix_log_path.sort()

        self.libano_log_path = []
        if isinstance(libano_log_path, str):
            self.libano_log_path = [libano_log_path]
        elif isinstance(libano_log_path, list):
            self.libano_log_path = libano_log_path
        self.libano_log_path.sort()

        temp_calibrator = InsideTemperatureCalibration()

        # read libano log files
        log_time = []
        log_outside_ap = []
        log_outside_sp = []
        libano_log = []
        last_sp = -1
        last_sp_index = 0
        n = 0
        for path in self.libano_log_path:
            libano_file = open(path, "r")
            while True:
                line = libano_file.readline().rstrip("\n")
                if line == "":
                    break
                k = line.split(";")
                time = dt.strptime(k[0], "%Y-%m-%dT%H:%M:%S%z").timestamp()
                cumulative_time = 0
                if int(k[1]) != last_sp:
                    last_sp = int(k[1])
                    last_sp_index = n
                else:
                    cumulative_time = time - libano_log[last_sp_index][0]
                log_time.append(time)
                log_outside_sp.append(int(k[1]))
                log_outside_ap.append(int(k[2]))
                try:
                    inside_temp = temp_calibrator.get_calibrated_temp(time=cumulative_time, sp=int(k[1]))
                except KeyError:
                    inside_temp = [0, 0]

                libano_log.append([time, int(k[1]), int(k[2]), cumulative_time, inside_temp[0], inside_temp[1]])
                n += 1

            libano_file.close()
        libano_log = np.array(libano_log).transpose()

        # # set time starts with zero
        # log_time = [i - log_time[0] for i in log_time]

        self.start_time = log_time[0]
        self.end_time = log_time[-1]

        # read helix log files
        helix_log = [[], [], [], [],  # start experiment, gas_in_end, gas_in, end experiment,
                     [], [], [], [], [], []],  # start_temp, s, end_temp, s, med_temp, s, sp, heating time
        helix_log = [[], [], [], [], [], [], [], [], [], [], [], []]
        nstep = 0

        keys = {
            "start_buildup": "GenWorkflow-BuildUp.cs: line 1: Clock reset",
            "set_temp": "GenWorkflow-Sampling.cs: Target temperature: key = Intensity, value = ",
            "end_sampling": "GenWorkflow-Prepare.cs: line 1: CLOSE for VUcleaningline/VINL2",
            "start_sampling": "GenWorkflow-Prepare.cs: line 14: CLOSE for VUcleaningline/VGP5",
            "end_sequence": "GenWorkflow-PostAcquisition.cs: line 7: Starting Acquisition",
            "get_setpoint": "GenWorkflow-Sampling.cs: Target temperature: key = Intensity, value = ",
        }

        # for Y56a
        if "Y56" in self.name:
            keys = {
                "start_buildup": "GenWorkflow-BuildUp.cs: line 1: Clock reset",
                "set_temp": "GenWorkflow-Sampling.cs: Target temperature: key = Intensity, value = ",
                "end_sampling": "GenWorkflow-Prepare.cs: line 1: CLOSE for VUcleaningline/VGP5",
                "start_sampling": "GenWorkflow-Sampling.cs: line 1: CLOSE for VUcleaningline/VGP5",
                "end_sequence": "GenWorkflow-PostAcquisition.cs: line 7: Starting Acquisition",
                "get_setpoint": "GenWorkflow-Sampling.cs: Target temperature: key = Intensity, value = ",
            }

        for file in self.helix_log_path:
            lines = open(file, 'r', encoding='utf-8-sig').readlines()
            for line in lines:

                if "|UserInfo|" not in line:
                    continue

                dt_str, helix, system, service, scripting, userinfo, message1, message2 = line.split("|")
                dt_utc = dt_str[:26] + dt_str[27:]
                dt_utc = dt.fromisoformat(str(dt_utc)).timestamp()

                if not (self.start_time <= dt_utc <= self.end_time):
                    continue
                if message1.startswith(keys["start_buildup"]):
                    ### start buildup
                    buildup_start = dt_utc
                    helix_log[0].append(dt_utc)
                if message1.startswith(keys["set_temp"]):
                    ### Close VGP5, not important
                    temp_value = message1.split(keys["get_setpoint"])[-1]
                    helix_log[10].append(int(temp_value))
                if message1.startswith(keys["end_sampling"]):
                    # 关闭vinlet2，60秒进质谱，之后开vinlet2，90秒抽气
                    gas_collection_end = dt_utc
                    helix_log[1].append(dt_utc)
                if message1.startswith(keys["start_sampling"]):
                    # Close VGP5, start peak centering and measurement, IMPORTANT: start to sampling
                    gas_collection_start = dt_utc
                    helix_log[2].append(dt_utc)
                if message1.startswith(keys["end_sequence"]):
                    # The End of the entire measurement
                    postacquisition_end = dt_utc
                    helix_log[3].append(dt_utc)
                    helix_log[4].append(0)
                    helix_log[5].append(0)
                    helix_log[6].append(0)
                    helix_log[7].append(0)
                    helix_log[8].append(0)
                    helix_log[9].append(0)
                    helix_log[11].append(0)
                    nstep += 1

        for i in helix_log:
            print(len(i))
            print(i)
        helix_log = np.array(helix_log)


        file_out = open(os.path.join(self.loc, f"{self.name}.txt"), "w")

        line = f"#\tSP\tHeatingTime\tCalibratedStartTemp\tError\tCalibratedEndTemp\tError\tCalibratedMedTemp\tError\n"
        file_out.writelines(line)

        yellow_data_index = []

        for i in range(nstep):
            if i == 0:
                gas_in_start = helix_log[0, 0]
            else:
                gas_in_start = helix_log[2, i - 1]

            # IMPORTANT, for Y56a
            if "Y56" in self.name:
                gas_in_start = helix_log[2, i]

            gas_in_end = helix_log[1, i]
            _index = [index for index, j in enumerate(libano_log[0]) if gas_in_start <= j <= gas_in_end]
            if len(_index) == 0:
                continue

            yellow_data_index.append(_index)

            med = int((_index[0] + _index[-1]) / 2)
            helix_log[4, i] = (libano_log[4, _index][0] + libano_log[5, _index][0]) / 2
            helix_log[5, i] = abs(libano_log[4, _index][0] - libano_log[5, _index][0]) / 2
            helix_log[6, i] = (libano_log[4, _index][-1] + libano_log[5, _index][-1]) / 2
            helix_log[7, i] = abs(libano_log[4, _index][-1] - libano_log[5, _index][-1]) / 2
            helix_log[8, i] = (libano_log[4, med] + libano_log[5, med]) / 2
            helix_log[9, i] = abs(libano_log[4, med] - libano_log[5, med]) / 2
            helix_log[11, i] = gas_in_end - gas_in_start

            line = f"{i + 1}\t{helix_log[10, i]}\t{helix_log[11, i]}\t" + '\t'.join(
                [str(j) for j in helix_log[4:10, i]]) + "\n"
            file_out.writelines(line)

        file_out.close()


        fig, ax = plt.subplots()
        fig.set_size_inches(w=12, h=10)

        ax.plot(libano_log[0], libano_log[1], c='green')
        ax.plot(libano_log[0], libano_log[2], c='blue')
        ax.plot(libano_log[0], libano_log[4], c='red')
        ax.plot(libano_log[0], libano_log[5], c='red')
        for i in range(nstep):
            _index = yellow_data_index[i]
            ax.plot(libano_log[0, _index], libano_log[4, _index], c='yellow')
            ax.plot(libano_log[0, _index], libano_log[5, _index], c='yellow')

        fig.tight_layout()
        plt.show()


        np.savetxt(os.path.join(self.loc, f"{self.name}-temp.txt"), libano_log, delimiter=',')
        heating_out = open(os.path.join(self.loc, f"{self.name}-heated-index.txt"), "w")
        heating_out.writelines([','.join([str(j) for j in i]) for i in yellow_data_index])
        heating_out.close()


        #
        # helix_times = self.read_helix_log()
        # gas_collection_start = helix_times['GasCollectionStart']
        # gas_collection_end = helix_times['GasCollectionEnd']
        # buildup_start = helix_times['01-Buildup-Time']
        # temperature_value = helix_times['Temperature Value']
        # postacquisiton_time = helix_times['10-Postacquisition-Part3-Time']
        #
        # temp_calibrator = ap.calc.diffusion_funcs.InsideTemperatureCalibration()
        #
        # heating_sequence = []
        # helix_log_data = [[], [], [], [], []]
        # last_sp = -1
        # for index, buildup in enumerate(buildup_start):
        #     sp = temperature_value[index]
        #     if index == 0:
        #         _start = buildup  # 收集气体的时间
        #     else:
        #         _start = gas_collection_start[index - 1]
        #
        #     gas_collection_time = gas_collection_end[index] - _start  # 收集气体的时间
        #
        #     if last_sp != sp:
        #         _before = _start - log_time[log_outside_sp.index(sp)]
        #         last_sp = sp
        #     else:
        #         _before = heating_sequence[index - 1]['cumulative_time'] + heating_sequence[index - 1]['heating_time'] / 2
        #     cumulative_time = gas_collection_time / 2 + _before
        #
        #     heating_sequence.append({
        #         "sp": sp, "heating_time": gas_collection_time, "cumulative_time": cumulative_time
        #     })
        #
        #     n = 50
        #     for i in range(n):
        #         helix_log_data[0].append(sp)  # sp
        #         helix_log_data[1].append(gas_collection_time / n * i + _before)  # cumulative_time
        #         try:
        #             if sp == 1500:
        #                 print(gas_collection_time / n * i + _before)
        #             k1, k2 = temp_calibrator.get_calibrated_temp(time=gas_collection_time / n * i + _before, sp=sp)
        #         except KeyError:
        #             pass
        #         else:
        #             helix_log_data[2].append(gas_collection_time * 1 / n + helix_log_data[2][-1] if len(helix_log_data[2]) >= 1 else gas_collection_time * 1 / n + _before)  # plot_time
        #             helix_log_data[3].append(k1)  # k1
        #             helix_log_data[4].append(k2)  # k2
        #
        #
        # file_out = open(os.path.join(self.loc, f"{self.name}.txt"), "w")
        #
        # line = f"#\tSP\tHeatingTime\tCalibratedTemp\tError\n"
        # file_out.writelines(line)
        #
        # log_inside_ap = []
        # log_inside_time = []
        # for index, temp in enumerate(heating_sequence):
        #     print(f"{temp}")
        #     try:
        #         k1, k2 = temp_calibrator.get_calibrated_temp(time=temp["cumulative_time"], sp=temp["sp"])
        #     except KeyError:
        #         k1 = -999
        #         k2 = -999
        #     else:
        #         log_inside_ap.append([k1, k2])
        #
        #     line = f"{index + 1}\t{temp['sp']}\t{temp['heating_time']}\t{round((k1 + k2) / 2, 0)}\t{round(abs(k2 - k1) / 2, 0)}\n"
        #     file_out.writelines(line)
        #
        #
        # file_out.close()
        #
        # fig, ax = plt.subplots()
        # fig.set_size_inches(w=12, h=10)
        # ax.plot([i - buildup_start[0] for i in log_time], log_outside_ap, c='blue')
        # ax.plot([i - buildup_start[0] for i in log_time], log_outside_sp, c='green')
        # ax.plot(helix_log_data[2], helix_log_data[3], c='red')
        # ax.plot(helix_log_data[2], helix_log_data[4], c='red')
        # fig.tight_layout()
        # plt.show()

    def read_helix_log(self):

        files = self.helix_log_path

        times = {
            "01-Buildup-Time": [],
            "02-Presampling-Time": [],
            "03-Sampling-Time": [],
            "GasCollectionStart": [],
            "05-Inlet-Time": [],
            "GasCollectionEnd": [],
            "07-Acquisition-Time": [],
            "08-Postacquisition-Part1-Time": [],
            "09-Postacquisition-Part2-Time": [],
            "10-Postacquisition-Part3-Time": [],
            "Temperature Value": []
        }

        for file in files:
            lines = open(file, 'r', encoding='utf-8-sig').readlines()
            for line in lines:
                if "|UserInfo|" not in line:
                    continue
                dt_str, helix, system, service, scripting, userinfo, message1, message2 = line.split("|")
                message2 = ""
                time = ""
                dt_utc = dt_str[:26] + dt_str[27:]
                dt_utc = dt.fromisoformat(str(dt_utc)).timestamp()
                if dt_utc < self.start_time or dt_utc > self.end_time:
                    continue
                if message1.startswith("GenWorkflow-BuildUp.cs: line 1: Clock reset"):
                    message2 = "10-Postacquisition-Part3-Time"
                    buildup_start = dt_utc
                    times[message2].append(dt_utc)
                if message1.startswith("GenWorkflow-Sampling.cs: line 1: OPEN for VUcleaningline/VGP1"):
                    message2 = "01-Buildup-Time"
                    times[message2].append(dt_utc)
                if message1.startswith("GenWorkflow-Sampling.cs: Target temperature: key = Intensity, value = "):
                    message2 = "Temperature Value"
                    temp_value = \
                    message1.split("GenWorkflow-Sampling.cs: Target temperature: key = Intensity, value = ")[-1]
                    times[message2].append(int(temp_value))
                # if message1.startswith("GenWorkflow-Sampling.cs: line 1: CLOSE for VUcleaningline/VGP5"):
                #     message2 = "02-Presampling-Time"
                #     times[message2].append(dt_utc)
                # if message1.startswith("GenWorkflow-Prepare.cs: line 1: CLOSE for VUcleaningline/VGP3"):
                #     message2 = "03-Sampling-Time"
                #     times[message2].append(dt_utc)
                if message1.startswith("GenWorkflow-Prepare.cs: line 1: CLOSE for VUcleaningline/VINL2"):
                    message2 = "GasCollectionEnd"
                    times[message2].append(dt_utc)
                # if message1.startswith("GenWorkflow-Prepare.cs: line 15: Starting Acquisition"):
                #     message2 = "05-Inlet-Time"
                #     times[message2].append(dt_utc)
                if message1.startswith("GenWorkflow-Prepare.cs: line 14: CLOSE for VUcleaningline/VGP5"):
                    message2 = "GasCollectionStart"
                    times[message2].append(dt_utc)
                # if message1.startswith("GenWorkflow-PostAcquisition.cs: line 1: OPEN for HelixMC/Valve Ion Pump Set"):
                #     message2 = "07-Acquisition-Time"
                #     times[message2].append(dt_utc)
                # if message1.startswith("GenWorkflow-PostAcquisition.cs: line 5: Starting Acquisition"):
                #     message2 = "08-Postacquisition-Part1-Time"
                #     times[message2].append(dt_utc)
                # if message1.startswith("GenWorkflow-PostAcquisition.cs: line 1: OPEN for VUcleaningline/VPIP"):
                #     message2 = "09-Postacquisition-Part2-Time"
                #     times[message2].append(dt_utc)

        return times


class ArrSmpMDD:

    def __init__(self, smp: Sample):
        self.smp = smp

    def initial(self, loc=""):
        if loc != "":
            self.diff = DiffSample(smp=self.smp, loc=loc)
        else:
            self.diff = DiffSample(smp=self.smp)

    def diffmulti(self, loc=""):
        if loc != "":
            self.diff_smp = DiffArrmultiFunc(smp=self.smp, loc=loc)
        else:
            self.diff_smp = DiffArrmultiFunc(smp=self.smp)
        k = self.diff_smp.main()

    def agemon(self, loc=""):
        if loc != "":
            self.diff_smp = DiffAgemonFuncs(smp=self.smp, loc=loc)
        else:
            self.diff_smp = DiffAgemonFuncs(smp=self.smp)
        k = self.diff_smp.main()

    def plot(self, loc=""):
        if loc != "":
            self.diff_smp = DiffDraw(smp=self.smp, loc=loc)
        else:
            self.diff_smp = DiffDraw(smp=self.smp)
        # self.diff_smp.loc = "D:\\PythonProjects\\ararpy_package\\ararpy\\examples"
        k = self.diff_smp.main()


class Ran1Generator:
    def __init__(self, idum):
        self.m1 = 259200
        self.ia1 = 7141
        self.ic1 = 54773
        self.rm1 = 3.8580247e-6

        self.m2 = 134456
        self.ia2 = 8121
        self.ic2 = 28411
        self.rm2 = 7.4373773e-6

        self.m3 = 243000
        self.ia3 = 4561
        self.ic3 = 51349

        self.r = np.zeros(97, dtype=np.float64)
        self.iff = 0
        self.ix1, self.ix2, self.ix3 = 0, 0, 0

        self.count = 0

        self.idum = idum
        self.initialize()

    def initialize(self):
        if self.idum < 0 or self.iff == 0:
            self.iff = 1
            self.ix1 = (self.ic1 - self.idum) % self.m1
            self.ix1 = (self.ia1 * self.ix1 + self.ic1) % self.m1
            self.ix2 = self.ix1 % self.m2
            self.ix1 = (self.ia1 * self.ix1 + self.ic1) % self.m1
            self.ix3 = self.ix1 % self.m3
            for j in range(97):
                self.ix1 = (self.ia1 * self.ix1 + self.ic1) % self.m1
                self.ix2 = (self.ia2 * self.ix2 + self.ic2) % self.m2
                self.r[j] = (float(self.ix1) + float(self.ix2) * self.rm2) * self.rm1
            self.idum = 1

    def ran1(self):
        # LCG算法生成随机数
        self.ix1 = (self.ia1 * self.ix1 + self.ic1) % self.m1
        self.ix2 = (self.ia2 * self.ix2 + self.ic2) % self.m2
        self.ix3 = (self.ia3 * self.ix3 + self.ic3) % self.m3
        j = 1 + int((97 * self.ix3) / self.m3)
        if j > 97 or j < 1:
            input('Press Enter to continue...')
        ran1 = self.r[j - 1]  # Adjust index for Python's 0-based indexing

        self.r[j - 1] = (float(self.ix1) + float(self.ix2) * self.rm2) * self.rm1

        self.count += 1

        print(f"{ran1 = }, {self.count = }")

        return ran1




def fit(x, y, sigx, sigy, ndata=None):

    print(f"{x = }")
    print(f"{y = }")
    print(f"{sigx = }")
    print(f"{sigy = }")

    if ndata is None:
        ndata = len(x)
    nd = 20
    imax = 20
    xerr = 0.001
    wt = []
    r = 0.
    a = 0
    b = -1.
    siga = 0
    sigb = 0
    chi2 = 0
    q = 0
    iter = 0

    while iter <= imax:
        sx = 0.
        sy = 0.
        st2 = 0.
        st3 = 0.
        ss = 0.
        b0 = b

        for i in range(ndata):
            wt.append(0)
            wt[i] = 1. / (sigy[i] ** 2 + b ** 2 * sigx[i] ** 2 - 2 * r * sigx[i] * sigy[i])
            ss = ss + wt[i]
            sx = sx + x[i] * wt[i]
            sy = sy + y[i] * wt[i]

            # print(f"{x[i] = }, {y[i] = }, {wt[i] = }")

        sxoss = sx / ss
        syoss = sy / ss

        for i in range(ndata):
            t1 = (x[i] - sxoss) * sigy[i] ** 2
            t2 = (y[i] - syoss) * sigx[i] ** 2 * b
            t3 = sigx[i] * sigy[i] * r
            st2 = st2 + wt[i] ** 2 * (y[i] - syoss) * (t1 + t2 - t3 * (y[i] - syoss))
            st3 = st3 + wt[i] ** 2 * (x[i] - sxoss) * (t1 + t2 - b * t3 * (x[i] - sxoss))

        b = st2 / st3
        iter = iter + 1

        # print(f"{sxoss = }, {syoss = }, {b = }, {abs(b0 - b) = }")

        if abs(b0 - b) > xerr:
            continue

        a = (syoss - sxoss * b)
        # print(f"{a = }, {b = }")
        sgt1 = 0.
        sgt2 = 0.

        for i in range(ndata):
            sgt1 = sgt1 + wt[i] * (x[i] - sxoss) ** 2
            sgt2 = sgt2 + wt[i] * x[i] ** 2

        sigb = (1. / sgt1) ** 0.5
        siga = sigb * (sgt2 / ss) ** 0.5
        chi2 = 0.

        for i in range(ndata):
            chi2 = chi2 + wt[i] * (y[i] - a - b * x[i]) ** 2

        q = gammq(0.5 * (ndata - 2), 0.5 * chi2)

        if abs(b0 - b) <= xerr:
            break

    return a, b, siga, sigb, chi2, q

def gammq(a, x):
    if x < 0 or a <= 0:
        raise ValueError("ERROR(GAMMQ): x < 0 or a <= 0")

    if x < a + 1:
        gamser, gln = gser(a, x)
        return 1.0 - gamser
    else:
        gammcf, gln = gcf(a, x)
        return gammcf

def gser(a, x, itmax=100, eps=3e-7):
    gln = gammln(a)
    if x <= 0:
        if x < 0:
            raise ValueError("ERROR(GSER): x < 0")
        return 0.0, gln

    ap = a
    sum_ = 1.0 / a
    delta = sum_
    for n in range(1, itmax + 1):
        ap += 1
        delta *= x / ap
        sum_ += delta
        if abs(delta) < abs(sum_) * eps:
            break
    else:
        raise RuntimeError("ERROR(GSER): a too large, itmax too small")

    gamser = sum_ * np.exp(-x + a * np.log(x) - gln)
    return gamser, gln

def gcf(a, x, itmax=100, eps=3e-7):
    gln = gammln(a)
    gold = 0.0
    a0 = 1.0
    a1 = x
    b0 = 0.0
    b1 = 1.0
    fac = 1.0
    for n in range(1, itmax + 1):
        an = float(n)
        ana = an - a
        a0 = (a1 + a0 * ana) * fac
        b0 = (b1 + b0 * ana) * fac
        anf = an * fac
        a1 = x * a0 + anf * a1
        b1 = x * b0 + anf * b1
        if a1 != 0:
            fac = 1.0 / a1
            g = b1 * fac
            if abs((g - gold) / g) < eps:
                return g * np.exp(-x + a * np.log(x) - gln), gln
            gold = g
    else:
        raise RuntimeError("ERROR(GCF): a too large, itmax too small")

def gammln(xx):
    cof = np.array([76.18009173, -86.50532033, 24.01409822,
                    -1.231739516, 0.00120858003, -0.00000536382])
    stp = 2.50662827465
    half = 0.5
    one = 1.0
    fpf = 5.5

    x = xx - one
    tmp = x + fpf
    tmp = (x + half) * np.log(tmp) - tmp
    ser = one
    for j in range(6):
        x += one
        ser += cof[j] / x

    return tmp + np.log(stp * ser)





def conf(input_x, input_y, count=None, num=None, using_binom=False, using_normal=False):
    """
    Calculate 90% confident interval of the given distribution of cooling histories.
    Parameters
    ----------
    input_x: x, array like 2D
    input_y: y, array like 2D
    count:

    Returns
    -------

    """

    input_x = np.array(input_x)
    input_y = np.array(input_y)

    if count is None:
        try:
            count = [input_x.shape[1]] * input_x.shape[0]
        except:
            return [], [], [], [], []

    x_start = min([min(xi) for xi in input_x])
    x_end = max([max(xi) for xi in input_x])
    x_steps_num = int(x_end - x_start) if num is None else num
    dx = (x_end - x_start) / x_steps_num

    x_conf = []
    y1_conf = []
    y2_conf = []
    y3_conf = []
    y4_conf = []

    for i in range(x_steps_num + 1):
        data = []
        # 置信曲线的x，即age
        xi = x_start + i * dx
        # 获取各个冷却曲线中对应age的温度temp，用临近两个年龄的斜率插值计算
        for j in range(len(input_x)):
            if xi > max(input_x[j]):
                continue
            yi = 0
            if xi == input_x[j, 0]:
                yi = input_y[j, 0]
            elif xi == input_x[j, count[j] - 1]:
                yi = input_y[j, count[j] - 1]
            else:
                for k in range(1, count[j]):
                    if (input_x[j, k] > xi >= input_x[j, k - 1]) or input_x[j, k - 1] > xi >= input_x[j, k]:
                        slope = (input_y[j, k] - input_y[j, k - 1]) / (input_x[j, k] - input_x[j, k - 1])
                        yi = input_y[j, k - 1] + slope * (xi - input_x[j, k - 1])
                        break
            data.append(yi)

        data = np.array(data)
        n = len(data)

        if n < 15:
            continue

        ave = np.average(data)
        dev = data - ave
        adev = sum(abs(dev)) / n
        var = sum(dev ** 2) / (n - 1)
        sdev = np.sqrt(var)
        skew = sum(dev ** 3) / (n * sdev ** 3) if var != 0 else 0
        curt = sum(dev ** 4) / (n * var ** 2) - 3 if var != 0 else 0

        # 中位数
        x_med = np.median(data)

        data.sort()

        if using_binom:
            # 计算二项分布百分位点
            try:
                j1, j2 = binom(n + 1)
            except ValueError:
                continue

            nperc = round(n * 0.05)

            x_conf.append(xi)
            y1_conf.append(data[j1 - 1])
            y2_conf.append(data[j2 - 1])
            y3_conf.append(data[int(nperc) - 1])
            y4_conf.append(data[int(n - nperc) - 1])

        elif using_normal:
            mean = np.mean(data)
            var = np.var(data)
            std = np.std(data)

            x_conf.append(xi)
            y1_conf.append(mean - std)
            y2_conf.append(mean + std)
            y3_conf.append(mean - 2 * std)
            y4_conf.append(mean + 2 * std)

    return x_conf, y1_conf, y2_conf, y3_conf, y4_conf


def binom(n):
    # 95% 置信区间百分位点

    def factln(n):
        return math.lgamma(n + 1)

    def bico(n, k):
        return math.exp(factln(n) - factln(k) - factln(n - k))

    if n % 2 == 0:
        nmed = n // 2
    else:
        nmed = (n + 1) // 2

    f = 0
    j1 = f

    # SEARCH FOR F(M)=0.5
    for j in range(nmed, 0, -1):
        faux = f
        f = 0.0
        j1 = j
        for k in range(1, j + 1):
            f += bico(n, k) * 0.5 ** n

        if f <= 0.05:
            if abs(faux - 0.05) < abs(f - 0.05):
                j1 = j1 + 1
            break

    for j in range(nmed + 1, n + 1):
        faux = f
        f = 0.0
        j2 = j
        for k in range(1, j + 1):
            f += bico(n, k) * 0.5 ** n

        if f >= 0.95:
            if abs(faux - 0.95) < abs(f - 0.95):
                j2 = j2 - 1
            return j1, j2

    raise ValueError("Error on binom subroutine")


def kahan_sum(input):
    sum = 0
    c = 0  # A running compensation for lost low-order bits.
    for i in input:
        y = i - c  # So far, so good: c is zero.
        t = sum + y  # Alas, sum is big, y small, so low-order digits of y are lost.
        c = (t - sum) - y  # (t - sum) recovers the high-order part of y; subtracting y recovers -(low part of y)
        sum = t  # Algebraically, c should always be zero. Beware eagerly optimising compilers!
    return sum


def get_random_index(length: int = 7):
    return ''.join(random.choices(string.digits, k=length))


def get_random_dir(path: str, length=7, random_index = ""):
    try:
        if random_index == "":
            random_index = get_random_index(length=length)
        destination_folder = os.path.join(path, random_index)
        os.makedirs(destination_folder, exist_ok=False)
        return destination_folder, random_index
    except FileExistsError:
        random_index = ""
        return get_random_dir(path=path, length=length)


def run_agemon_dll(sample: Sample, source_dll_path: str, loc: str, data, max_age: float = 30.):
    # 加载 DLL
    # 获取源 DLL 文件名和扩展名
    base_name, ext = os.path.splitext(os.path.basename(source_dll_path))
    # 构建新的 DLL 文件名
    new_dll_path = os.path.join(loc, f"{base_name}{ext}")
    # 复制并重命名 DLL 文件
    shutil.copy(source_dll_path, new_dll_path)

    agemon = DiffAgemonFuncs(smp=sample, loc=loc)

    agemon.ni = len(data)
    agemon.nit = agemon.ni
    agemon.max_plateau_age = max_age
    data = ap.calc.arr.transpose(data)
    agemon.telab = [i + 273.15 for i in data[3]]
    agemon.tilab = [i / 5.256E+11 for i in data[4]]  # 1 Ma = 525600000000 minutes
    for i in range(agemon.nit):
        if agemon.telab[i] > 1373:
            agemon.ni = i
            break
    agemon.ya = data[5]
    agemon.sig = data[6]
    agemon.a39 = data[7]
    agemon.sig39 = data[8]
    agemon.xs = data[9]
    agemon.xs.insert(0, 0)
    agemon.ya.insert(0, 0)

    agemon.xs = np.array(agemon.xs)
    agemon.xs = np.where(agemon.xs >= 1, 0.9999999999999999, agemon.xs)
    # agemon.xs[-1] = 0.9999999999999999 if agemon.xs[-1] >= 1 else agemon.xs[-1]

    xs = agemon.xs  # array
    age = agemon.ya  # array
    sig = agemon.sig  # array
    e = agemon.e_arr  # array
    d0 = agemon.d0_arr  # array
    vc = agemon.vc_arr  # array
    nsts = agemon.nst_arr  # array
    temp = agemon.telab  # array
    heating_time = agemon.tilab  # array
    kk = agemon.kk  # int
    max_age = agemon.max_plateau_age  # double
    nsteps = agemon.ni  # int

    # print(f"{xs = }")
    # print(f"{age = }")
    # print(f"{sig = }")
    # print(f"{e = }")
    # print(f"{d0 = }")
    # print(f"{vc = }")
    # print(f"{nsts = }")
    # print(f"{temp = }")
    # print(f"{heating_time = }")
    # print(f"{kk = }")
    # print(f"{max_age = }")
    # print(f"{nsteps = }")

    d0_flatten = d0.flatten()
    vc_flatten = vc.flatten()

    # filepath = "D:\\DjangoProjects\\webarar\\private\\mdd"
    # print(filepath.encode())
    filepath = bytes(loc, "utf-8")
    samplename = bytes(sample.name(), "utf-8")

    mylib = ctypes.CDLL(new_dll_path)
    try:
        run = mylib.run
        run.restype = None
        result = run(
            (ctypes.c_double * len(xs))(*xs), ctypes.c_int(len(xs)),
            (ctypes.c_double * len(age))(*age), ctypes.c_int(len(age)),
            (ctypes.c_double * len(sig))(*sig), ctypes.c_int(len(sig)),
            (ctypes.c_double * len(e))(*e), ctypes.c_int(len(e)),
            (ctypes.c_double * len(d0_flatten))(*d0_flatten), ctypes.c_int(d0.shape[0]), ctypes.c_int(d0.shape[1]),
            (ctypes.c_double * len(vc_flatten))(*vc_flatten), ctypes.c_int(vc.shape[0]), ctypes.c_int(vc.shape[1]),
            (ctypes.c_int * len(nsts))(*nsts), ctypes.c_int(len(nsts)),
            (ctypes.c_double * len(temp))(*temp), ctypes.c_int(len(temp)),
            (ctypes.c_double * len(heating_time))(*heating_time), ctypes.c_int(len(heating_time)),
            ctypes.c_int(kk),
            ctypes.c_double(max_age),
            ctypes.c_int(nsteps),
            ctypes.c_char_p(filepath),
            ctypes.c_char_p(samplename)
        )
    except:
        pass
    else:
        del mylib
        gc.collect()

    return


def dr2_popov(f, ti):
    """

    Parameters
    ----------
    f: cumulative 39Ar released, array
    ti: heating time, array

    Returns
    -------

    """

    # =IF(M4<85,(   (-6/(PI()^(3/2))+SQRT(36/(PI()^3)-4*M4/100*3/(PI()^2)))/(-6/(PI()^2)))^2/(PI()^2    )/D4/60,(LN(((M4)/100-1)/(-6/PI()^2))/(-PI()^2))/D4/60)

    # =IF(M5<85,(    2/PI()^2*( SQRT(PI()^2-(PI()^3)*M4/100/3)-SQRT(PI()^2-(PI()^3)*M5/100/3)) +M4/100/3-M5/100/3 )/D5/60,     LN((1-M4/100)/(1-M5/100))/PI()^2/D5/60)

    f = np.array(f)
    ti = np.array(ti)
    n = min(len(f), len(ti))
    ti = ti * 60  # in seconds
    pi = math.pi
    pi = 3.141592654
    dr2 = np.zeros(n)

    if f[-1] >= 1:
        f[-1] = 0.99999999

    # Popov 2020
    a, b = 0, 0
    for i in range(len(f)):
        if i == 0:
            if f[i] < 85:
                a = 2 / pi ** 2 * math.sqrt(pi ** 2 - (pi ** 3) * f[i] / 3) + f[i] / 3
                dr2[i] = ((-6 / (pi ** 1.5) + math.sqrt(36 / pi ** 3 - 4 * f[i] * 3 / pi ** 2)) / (
                            -6 / pi ** 2)) ** 2 / pi ** 2 / ti[i]
            else:
                a = 1 - f[i]
                dr2[i] = (math.log((f[i] - 1) / (-6 / pi ** 2)) / pi ** 2) / ti[i]
        else:
            if f[i] < 85:
                a = 2 / pi ** 2 * math.sqrt(pi ** 2 - (pi ** 3) * f[i] / 3) + f[i] / 3
                dr2[i] = (b - a) / ti[i]
            else:
                dr2[i] = math.log((1 - f[i - 1]) / (1 - f[i])) / pi ** 2 / ti[i]
        b = a

    print(f"popov {dr2 = }")

    return dr2, np.log(dr2)


def dr2_lovera(f, ti, ar, sar):
    # Lovera
    f = np.array(f)
    ti = np.array(ti)
    ar = np.array(ar)
    sar = np.array(sar)
    ti = ti * 60  # in seconds
    pi = math.pi
    pi = 3.141592654

    # sf = sqrt(b ** 2 * siga ** 2 + a ** 2 * sigb ** 2) / (a + b) ** 2
    sf = [math.sqrt(sar[i + 1:].sum() ** 2 * (sar[:i + 1] ** 2).sum() + ar[:i + 1].sum() ** 2 * (sar[i + 1:] ** 2).sum()) / ar.sum() ** 2 for i in range(len(ar) - 1)]
    sf.append(0)

    f = np.where(f >= 1, 0.9999999999999999, f)

    imp = 2
    # imp = 1
    dtr2 = [pi * (fi / 4) ** 2 if fi <= 0.5 else math.log((1 - fi) * pi ** 2 / 8) / (- pi ** 2) for fi in f]
    dr2 = [(dtr2[i] - (dtr2[i - 1] if i > 0 else 0)) / ti[i] * imp ** 2 for i in range(len(dtr2))]
    xlogd = [np.log10(i) for i in dr2]

    wt = errcal(f, ti, a39=ar, sig39=sar)

    return dr2, xlogd, wt


def dr2_yang(f, ti):
    f = np.array(f)
    ti = np.array(ti)
    n = min(len(f), len(ti))
    ti = ti * 60  # in seconds
    pi = math.pi
    pi = 3.141592654
    dr2 = np.zeros(n)

    if f[-1] >= 1:
        f[-1] = 0.99999999

    def _dr2(_fi):
        if _fi <= 0.85:
            return (1 - math.sqrt(1 - pi * _fi / 3)) ** 2 / pi
        else:
            return math.log((1 - _fi) / (6 / pi ** 2)) / - (pi ** 2)

    for i in range(len(f)):
        if i == 0:
            dr2[i] = _dr2(f[i]) / ti[i]
        else:
            dr2[i] = _dr2((f[i] - f[i - 1]) / (1 - f[i - 1])) / ti[i]

    print(f"yang {dr2 = }")

    return dr2, np.log(dr2)


def errcal(f, ti, a39, sig39):

    # ns = 200
    # r = 1.987E-3
    # a0 = -0.19354
    # a1 = -0.62946
    # a2 = 0.13505
    # a3 = -0.01528

    f = np.array(f)
    ti = np.array(ti)  # in seconds

    ee = 0.4342944819
    sigt0 = 90.

    ni = len(f)
    sumat = sum(a39)
    sigsm = [i / sumat for i in sig39]
    siga = [sig39[i] / a39[i] for i in range(ni)]

    an1 = math.pi ** 2
    sigat = 0.
    swt = 0.
    sigzit = [0.]
    sigf = [0]
    wt = []

    for i in range(ni):
        sigat += sigsm[i] ** 2
        sigf.append(sigat)

    f = np.insert(f, 0, 0)

    for i in range(1, ni + 1):
        sigzit.append(0)
        if f[i] <= 0.5:
            fp = f[i] + f[i - 1]
            as1 = 1. / fp ** 2 - 2. / fp
            as2 = (f[i] ** 2 - 2 * f[i] * (f[i] ** 2 - f[i - 1] ** 2)) / fp ** 2
            sigzit[i] = 4. * (sigat + sigf[i - 1] * as1 + siga[i - 1] ** 2 * as2)
        else:
            dzit2 = (np.log((1 - f[i]) / (1 - f[i - 1])) / an1) ** 2
            as1 = ((f[i] - f[i - 1]) / an1) ** 2 / (1 - f[i - 1]) ** 2
            sigzit[i] = ((sigat - sigf[i]) / (1 - f[i]) ** 2 + siga[i - 1] ** 2) * as1
            sigzit[i] = sigzit[i] / dzit2

    print(f"{sigzit = }")

    for i in range(ni):
        sigt = (sigt0 / ti[i]) ** 2
        wt.append(ee * (sigt + sigzit[i + 1]) ** 0.5)
        swt = swt + wt[i]
        rate = (sigzit[i + 1] / sigt) ** 0.5

    print(f"lovera {wt = }")


    ## 下面是我重新改写 计算的  与lovera的结果接近但不一致

    # a39 = np.insert(a39, 0, 0)
    # sig39 = np.insert(sig39, 0, 0)
    #
    # wt = []
    # for i in range(0, ni):
    #
    #     if f[i + 1] <= 0.5:
    #         sigt = (sigt0 / ti[i]) ** 2
    #         fp = (f[i + 1] + f[i])
    #         a = sig39[i + 1] / a39[i + 1]
    #         wt.append(ee * (sigt + 4 * (a ** 2 - 2 * a / a39.sum() + sigat) / (a39.sum() * fp) ** 2) ** 0.5)
    #     else:
    #         sigt = (sigt0 / ti[i]) ** 2
    #         sigf = (a39[i + 1] ** 2 / a39[i + 2:].sum() ** 2 * sig39[i + 2:].sum() ** 2 + sig39[i + 1] ** 2) / a39[i + 1:].sum() ** 2
    #         wt.append(ee * (sigt + (1 / math.log((1 - f[i + 1]) / (1 - f[i]))) ** 2 * sigf) ** 0.5)
    #
    # print(f"new function {wt = }")

    return wt
