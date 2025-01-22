import copy
import os
import json
import pickle
import traceback
import re
import numpy as np
import pdf_maker as pm
import uuid

# from math import ceil
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from . import models
from programs import http_funcs, log_funcs, ap
from django.core.cache import cache


# Create your views here.
class CalcHtmlView(http_funcs.ArArView):
    """
    Views on calc.html, responses to command of opening files based on flags.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatch_post_method_name = [
            "open_raw_file",
            "open_arr_file",
            "open_full_xls_file",
            "open_age_file",
            "open_current_file",
            "open_new_file",
            "open_multi_files",
            "update_sample_photo"
        ]

    def open_raw_file(self, request, *args, **kwargs):
        log_funcs.set_info_log(self.ip, '001', 'info', 'Open raw file')
        return redirect('open_raw_file_filter')

    def open_arr_file(self, request, *args, **kwargs):
        log_funcs.set_info_log(self.ip, '001', 'info', 'Open arr file')
        try:
            web_file_path, file_name, extension = \
                ap.files.basic.upload(request.FILES.get('arr_file'), settings.UPLOAD_ROOT)
            # sample = file_funcs.open_arr_file(web_file_path)
            sample = ap.from_arr(web_file_path)
        except (Exception, BaseException) as e:
            print(traceback.format_exc())
            return render(request, 'calc.html', {
                'title': 'alert', 'type': 'Error', 'msg': 'Fail to open the arr file\n' + str(e)
            })
        else:
            return http_funcs.open_object_file(request, sample, web_file_path)

    def open_full_xls_file(self, request, *args, **kwargs):
        log_funcs.set_info_log(self.ip, '001', 'info', 'Open calc.full file')
        try:
            web_file_path, file_name, extension = \
                ap.files.basic.upload(request.FILES.get('full_xls_file'), settings.UPLOAD_ROOT)
            file_name = file_name if '.full' not in file_name else file_name.split('.full')[0]
            sample = ap.from_full(file_path=web_file_path, sample_name=file_name)
            sample.recalculate(re_plot=True, re_plot_style=True, re_set_table=True, re_table_style=True)
        except (Exception, BaseException) as e:
            return render(request, 'calc.html', {
                'title': 'alert', 'type': 'Error', 'msg': 'Fail to open the xls file\n' + str(e)
            })
        else:
            return http_funcs.open_object_file(request, sample, web_file_path)

    def open_age_file(self, request, *args, **kwargs):
        log_funcs.set_info_log(self.ip, '001', 'info', 'Open calc.age file')
        try:
            web_file_path, sample_name, extension = \
                ap.files.basic.upload(request.FILES.get('age_file'), settings.UPLOAD_ROOT)
            # sample = file_funcs.open_age_xls(web_file_path)
            sample = ap.from_age(file_path=web_file_path, sample_name=sample_name)
            try:
                # Re-calculating ratio and plot after reading age or full files
                sample.recalculate(re_calc_ratio=True, re_plot=True, re_plot_style=True, re_set_table=True)
                # ap.recalculate(sample, re_calc_ratio=True, re_plot=True, re_plot_style=True, re_set_table=True)
            except Exception as e:
                print(f'Error in setting plot: {traceback.format_exc()}')
        except (Exception, BaseException) as e:
            print(traceback.format_exc())
            return render(request, 'calc.html', {
                'title': 'alert', 'type': 'Error', 'msg': 'Fail to open the age file\n' + str(e)
            })
        else:
            return http_funcs.open_object_file(request, sample, web_file_path)

    def open_current_file(self, request, *args, **kwargs):
        log_funcs.set_info_log(self.ip, '001', 'info', 'Open last file')
        return http_funcs.open_last_object(request)

    def open_new_file(self, request, *args, **kwargs):
        log_funcs.set_info_log(self.ip, '001', 'info', 'Open new file')
        sample = ap.from_empty()
        return http_funcs.open_object_file(request, sample, web_file_path='')

    def open_multi_files(self, request, *args, **kwargs):
        msg = ""
        length = int(request.POST.get('length'))
        # print(f"Number of files: {length}")
        files = {}
        for i in range(length):
            file = request.FILES.get(str(i))
            try:
                web_file_path, file_name, suffix = ap.files.basic.upload(
                    file, settings.UPLOAD_ROOT)
            except (Exception, BaseException) as e:
                msg = msg + f"{file} is not supported. "
                continue
            else:
                files.update({f"multi_files_{i}": {'name': file_name, 'path': web_file_path, 'suffix': suffix}})
        response = HttpResponse(content_type="text/html; charset=utf-8", status=299)
        contents = []
        for key, file in files.items():
            handler = {
                '.arr': ap.from_arr, '.xls': ap.from_full, '.age': ap.from_age
            }.get(file['suffix'], None)
            try:
                if handler:
                    sample = handler(file['path'], **{'file_name': file['name']})
                else:
                    raise TypeError(f"File type {file['suffix']} is not supported: {file['name']}")
            except Exception:
                print(traceback.format_exc())
                continue
            else:
                contents.append(http_funcs.open_object_file(request, sample, file['path']).component)
        response.writelines(contents)
        return response

    @staticmethod
    def get(request, *args, **kwargs):
        # Render calc.html when users are visiting /calc.
        return render(request, 'calc.html')

    def flag_not_matched(self, request, *args, **kwargs):
        # Show calc.html when the received flag doesn't exist.
        log_funcs.set_info_log(self.ip, '001', 'warning', f'Received flag: {self.flag}, it is not matched')
        return render(request, 'calc.html')


class ButtonsResponseObjectView(http_funcs.ArArView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatch_post_method_name = [
        ]

    def get(self, request, *args, **kwargs):
        # Visiting /calc/object
        log_funcs.set_info_log(self.ip, '003', 'info', f'GET /calc/object')
        return http_funcs.open_last_object(request)

    def update_sample_photo(self, request, *args, **kwargs):
        log_funcs.set_info_log(self.ip, '003', 'info', 'Update sample photo')
        file = request.FILES.get('picture')
        ap.files.basic.upload(file, os.path.join(settings.STATICFILES_DIRS[0], 'upload'))
        return JsonResponse({'picture': settings.STATIC_URL + 'upload/' + file.name})

    def get_auto_scale(self, request, *args, **kwargs):
        figure_id = self.body['figure_id']
        xscale, yscale = ap.smp.style.reset_plot_scale(smp=self.sample, only_figure=figure_id)
        return JsonResponse({
            'status': 'success', 'xMin': xscale[0], 'xMax': xscale[1], 'xInterval': xscale[2],
            'yMin': yscale[0], 'yMax': yscale[1], 'yInterval': yscale[2]
        })

    def update_components_diff(self, request, *args, **kwargs):
        diff = dict(self.body['diff'])
        # print(f"{diff = }")
        for name, attrs in diff.items():
            ap.smp.basic.update_object_from_dict(
                ap.smp.basic.get_component_byid(self.sample, name), attrs)

        self.sample.SequenceName = [v[0] for i, v in enumerate(self.sample.IsochronsTable.data)]
        self.sample.SequenceValue = [v[1] for i, v in enumerate(self.sample.IsochronsTable.data)]
        self.sample.IsochronMark = [v[2] for i, v in enumerate(self.sample.IsochronsTable.data)]

        ap.smp.table.update_data_from_table(self.sample)

        # self.sample.UnknownTable.data = ap.calc.arr.transpose(self.sample.UnknownTable.data)
        # self.sample.BlankTable.data = ap.calc.arr.transpose(self.sample.BlankTable.data)
        # self.sample.CorrectedTable.data = ap.calc.arr.transpose(self.sample.CorrectedTable.data)
        # self.sample.DegasPatternTable.data = ap.calc.arr.transpose(self.sample.DegasPatternTable.data)
        # self.sample.PublishTable.data = ap.calc.arr.transpose(self.sample.PublishTable.data)
        # self.sample.AgeSpectraPlot.data = ap.calc.arr.transpose(self.sample.AgeSpectraPlot.data)
        # self.sample.IsochronsTable.data = ap.calc.arr.transpose(self.sample.IsochronsTable.data)
        # self.sample.TotalParamsTable.data = ap.calc.arr.transpose(self.sample.TotalParamsTable.data)

        res = {}
        if 'figure_9' in diff.keys() and not all(
                [i not in diff.get('figure_9').keys() for i in ['set1', 'set2', 'set3']]):
            # Backup after changes are applied
            components_backup = copy.deepcopy(ap.smp.basic.get_components(self.sample))
            # Histogram plot, replot is required
            ap.smp.plots.recalc_agedistribution(self.sample)
            res = ap.smp.basic.get_diff_smp(backup=components_backup, smp=ap.smp.basic.get_components(self.sample))

        # 2024/04/10
        self.sample.SelectedSequence1 = [
            i for i in range(len(self.sample.IsochronMark)) if str(self.sample.IsochronMark[i]) == "1"]
        self.sample.SelectedSequence2 = [
            i for i in range(len(self.sample.IsochronMark)) if str(self.sample.IsochronMark[i]) == "2"]
        self.sample.UnselectedSequence = [
            i for i in range(len(self.sample.IsochronMark)) if
            i not in self.sample.SelectedSequence1 + self.sample.SelectedSequence2]
        # self.sample.SelectedSequence1 = self.sample.InvIsochronPlot.set1.data.copy()
        # self.sample.SelectedSequence2 = self.sample.InvIsochronPlot.set2.data.copy()
        # self.sample.UnselectedSequence = self.sample.InvIsochronPlot.set3.data.copy()

        self.sample.Info.results.selection[0]['data'] = self.sample.SelectedSequence1
        self.sample.Info.results.selection[1]['data'] = self.sample.SelectedSequence2
        self.sample.Info.results.selection[2]['data'] = self.sample.UnselectedSequence

        http_funcs.create_cache(self.sample, self.cache_key)  # Update cache
        return JsonResponse(res)

    def click_points_update_figures(self, request, *args, **kwargs):

        clicked_data = self.content['clicked_data']
        current_set = self.content['current_set']
        auto_replot = self.content['auto_replot']
        figures = self.content.pop('figures',
                                   ['figure_2', 'figure_3', 'figure_4', 'figure_5', 'figure_6', 'figure_7', ])
        sample = self.sample
        components_backup = copy.deepcopy(ap.smp.basic.get_components(sample))
        # print(f"{sample.IsochronMark = }")

        data_index = clicked_data[-1] - 1  # Isochron plot data label starts from 1, not 0
        sample.set_selection(data_index, [1, 2][current_set == "set2"])

        if auto_replot:
            # Re-plot after clicking points
            sample.recalculate(re_plot=True, isInit=False, isIsochron=True, isPlateau=False, figures=figures)
            # ap.recalculate(sample, re_plot=True, isInit=False, isIsochron=True, isPlateau=True)

        # Response are changes in sample.Components, in this way we can decrease the size of response.
        res = ap.smp.basic.get_diff_smp(
            backup=components_backup, smp=ap.smp.basic.get_components(sample))
        # Update isochron table data, changes in isotope table is not required to transfer
        ap.smp.table.update_table_data(sample, only_table='7')
        http_funcs.create_cache(sample, self.cache_key)  # 更新缓存
        # print(f"在点击事件结束之后 {sample.IsochronMark = }")

        return JsonResponse({'res': ap.smp.json.dumps(res)})

    def update_handsontable(self, request, *args, **kwargs):
        btn_id = str(self.body['btn_id'])
        recalculate = self.body['recalculate']  # This is always False
        data = self.body['data']
        sample = self.sample
        log_funcs.set_info_log(
            self.ip, '003', 'info',
            f'Update handsontable, sample name: {sample.Info.sample.name}, btn id: {btn_id}'
        )
        # backup for later comparision
        components_backup = copy.deepcopy(ap.smp.basic.get_components(sample))
        if btn_id == '0':  # 实验信息
            # sample.Info.__dict__.update(data)
            ap.smp.basic.update_plot_from_dict(sample.Info, data)
        else:

            def remove_empty(a: list):
                index = 0
                for i in range(len(a)):
                    if not ap.calc.arr.is_empty(a[-(i + 1)]):
                        index = len(a) - i
                        break
                return ap.calc.arr.transpose(a[:index])

            data = remove_empty(data)
            if len(data) == 0:
                return JsonResponse({})

            sample.update_table(data, btn_id)

            if btn_id == '7':
                # Re-calculate isochron and plateau data, and replot.
                # Re-calculation will not be applied automatically when other tables were changed
                sample.recalculate(re_plot=True, isInit=False, isIsochron=True, isPlateau=True)
                # ap.recalculate(sample, re_plot=True, isInit=False, isIsochron=True, isPlateau=True)

        http_funcs.create_cache(sample, self.cache_key)  # Update cache
        res = ap.smp.basic.get_diff_smp(components_backup, ap.smp.basic.get_components(sample))
        return JsonResponse({'changed_components': ap.smp.json.dumps(res)})

    def get_regression_result(self, request, *args, **kwargs):
        data = list(self.body.get('data'))
        method = str(self.body.get('method'))
        adjusted_x = list(self.body.get('x'))

        x, adjusted_time = [], []
        year, month, day, hour, min, second = re.findall(r"\d+", data[0][0])[0]
        for each in data[0]:
            x.append(ap.calc.basic.get_datetime(
                *re.findall(r"\d+", each)[0],
                base=[int(year), int(month), int(day), int(hour), int(min)]
            ))
        for each in adjusted_x:
            adjusted_time.append(ap.calc.basic.get_datetime(*re.findall(r"\d+", each)[0],
                base=[int(year), int(month), int(day), int(hour), int(min)]
            ))
        y = data[1]
        x, y = zip(*sorted(zip(x, y), key=lambda _x: _x[0]))
        handler = {
            'linear': ap.calc.regression.linest,
            'average': ap.calc.regression.average,
            'quadratic': ap.calc.regression.quadratic,
            'polynomial': ap.calc.regression.polynomial,
            'power': ap.calc.regression.power,
            'exponential': ap.calc.regression.exponential,
        }
        if method in handler.keys():
            try:
                handler = handler[method]
                res = handler(y, x)
            except:
                print(traceback.format_exc())
                res = False
            if res:
                line_data = [adjusted_x, res[7](adjusted_time)]
                return JsonResponse({'r2': res[3], 'line_data': line_data, 'sey': res[8]})
        return JsonResponse({'r2': 'None', 'line_data': [], 'sey': 'None'})

    def set_params(self, request, *args, **kwargs):
        def remove_none(old_params, new_params, rows, length):
            res = [[]] * length
            for index, item in enumerate(new_params):
                if item is None:
                    res[index] = old_params[index]
                else:
                    res[index] = [item] * rows
            return res

        params = list(self.body['params'])
        type = str(self.body['type'])  # type = 'irra', or 'calc', or 'smp'
        sample = self.sample
        log_funcs.set_info_log(
            self.ip, '003', 'info', f'Set params, sample name: {self.sample.Info.sample.name}')
        # backup for later comparision
        components_backup = copy.deepcopy(ap.smp.basic.get_components(sample))

        try:
            sample.set_params(params, type)
        except KeyError:
            return JsonResponse({'status': 'fail', 'msg': f'Unknown type of params : {type}'})

        ap.smp.table.update_table_data(sample)  # Update data of tables after changes of calculation parameters
        # update cache
        http_funcs.create_cache(sample, self.cache_key)
        res = ap.smp.basic.get_diff_smp(backup=components_backup, smp=ap.smp.basic.get_components(sample))
        # print(f"Diff after reset_calc_params: {res}")
        return JsonResponse(
            {'status': 'success', 'msg': 'Successfully!', 'changed_components': ap.smp.json.dumps(res)})

    def recalculation(self, request, *args, **kwargs):
        log_funcs.set_info_log(self.ip, '003', 'info', f'Recalculation, sample name: {self.sample.Info.sample.name}')
        sample = self.sample
        checked_options = self.content['checked_options']
        others = self.content.pop('others', {})
        isochron_mark = self.content.pop('isochron_mark', False)
        # print(f"Recalculation Isochron Mark = {isochron_mark}")
        if isochron_mark:
            sample.IsochronMark = isochron_mark.copy()
            sample.SelectedSequence1 = [index for index, item in enumerate(isochron_mark) if str(item) == '1']
            sample.SelectedSequence2 = [index for index, item in enumerate(isochron_mark) if str(item) == '2']
            sample.UnselectedSequence = [index for index, item in enumerate(isochron_mark) if str(item) != '2' and str(item) != '1']
            sample.Info.results.selection[0]['data'] = sample.SelectedSequence1
            sample.Info.results.selection[1]['data'] = sample.SelectedSequence2
            sample.Info.results.selection[2]['data'] = sample.UnselectedSequence
        # backup for later comparision
        components_backup = copy.deepcopy(ap.smp.basic.get_components(sample))
        try:
            # Re-calculating based on selected options
            sample.recalculate(*checked_options, **others)
            # sample = ap.recalculate(sample, *checked_options)
        except Exception as e:
            log_funcs.log(traceback.format_exc())
            return JsonResponse({'msg': f'Error in recalculating: {e}'}, status=403)
        ap.smp.table.update_table_data(sample)  # Update data of tables after re-calculation
        # Update cache
        http_funcs.create_cache(sample, self.cache_key)
        res = ap.smp.basic.get_diff_smp(backup=components_backup, smp=ap.smp.basic.get_components(sample))
        return JsonResponse({'msg': "Success to recalculate", 'res': ap.smp.json.dumps(res)})

    def flag_not_matched(self, request, *args, **kwargs):
        # Show calc.html when the received flag doesn't exist.
        return http_funcs.open_last_object(request)


class RawFileView(http_funcs.ArArView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatch_post_method_name = [
            "submit",
            'close',
            'to_project_view',
            'raw_data_submit',
        ]

    def get(self, request, *args, **kwargs):
        # Visiting /calc/raw
        log_funcs.set_info_log(self.ip, '004', 'info', f'Open raw file filter')
        return render(request, 'raw_filter.html')

    def flag_not_matched(self, request, *args, **kwargs):
        log_funcs.set_info_log(self.ip, '004', 'info', f'Flag is not matched')
        return redirect('calc_view')

    def close(self, request, *args, **kwargs):
        log_funcs.set_info_log(self.ip, '004', 'info', f'Close')
        return redirect('calc_view')

    def raw_files_changed(self, request, *args, **kwargs):
        files = []
        names = list(models.InputFilterParams.objects.values_list('name', flat=True))
        for file in request.FILES.getlist('raw_file'):
            try:
                web_file_path, file_name, suffix = ap.files.basic.upload(
                    file, settings.UPLOAD_ROOT)
            except (Exception, BaseException):
                continue
            else:
                files.append({
                    'name': file_name, 'extension': suffix, 'path': web_file_path,
                    'filter': suffix[1:],
                    'filter_list': names
                })
        return JsonResponse({'files': files})

    def submit(self, request, *args, **kwargs):
        files = json.loads(request.POST.get('raw-file-table'))['files']
        file_path = [each['file_path'] for each in files if each['checked']]
        filter_name = [each['filter'] for each in files if each['checked']]
        filter_paths = [getattr(models, "InputFilterParams").objects.get(name=each).file_path for each in filter_name]
        try:
            raw = ap.smp.raw.to_raw(file_path=file_path, input_filter_path=filter_paths)
            print("before do regression")
            raw.do_regression()

            allIrraNames = list(models.IrraParams.objects.values_list('name', flat=True))
            allCalcNames = list(models.CalcParams.objects.values_list('name', flat=True))
            allSmpNames = list(models.SmpParams.objects.values_list('name', flat=True))

            # update cache
            cache_key = http_funcs.create_cache(raw)
            return render(request, 'extrapolate.html', {
                'raw_data': ap.smp.json.dumps(raw), 'raw_cache_key': ap.smp.json.dumps(cache_key),
                'allIrraNames': allIrraNames, 'allCalcNames': allCalcNames, 'allSmpNames': allSmpNames
            })
        except FileNotFoundError as e:
            messages.error(request, e)
        except ValueError as e:
            print(traceback.format_exc())
            messages.error(request, e)
        except (Exception, BaseException):
            print(traceback.format_exc())
            messages.error(request, traceback.format_exc())
        print("Render")
        return render(request, 'raw_filter.html')

    def import_blank_file(self, request, *args, **kwargs):
        file = request.FILES.get('blank_file')
        cache_key = request.POST.get('cache_key')
        raw: ap.RawData = pickle.loads(cache.get(cache_key))

        web_file_path, file_name, suffix = ap.files.basic.upload(
            file, settings.UPLOAD_ROOT)
        try:
            with open(web_file_path, 'rb') as f:
                sequences = pickle.load(f)
        except pickle.UnpicklingError:
            return JsonResponse({
                'msg': "The file input cannot be unpicked. Please check the file format"},
                encoder=ap.smp.json.MyEncoder, status=403)

        raw.sequence = ap.calc.arr.multi_append(raw.sequence, *sequences)
        http_funcs.create_cache(raw, cache_key=cache_key)

        return JsonResponse({'sequences': sequences}, encoder=ap.smp.json.MyEncoder,
                            content_type='application/json', safe=True)

    def add_empty_blank(self, request, *args, **kwargs):
        raw: ap.RawData = self.sample
        new_blank_sequence = {
            'name': ['EMPTY'],
            'experimentTime': "1996-08-09T08:00:00",
            'Ar36': [[0, 0, 0, 0]],
            'Ar37': [[0, 0, 0, 0]],
            'Ar38': [[0, 0, 0, 0]],
            'Ar39': [[0, 0, 0, 0]],
            'Ar40': [[0, 0, 0, 0]],
        }
        new_sequence = ap.Sequence(
            index='undefined', name=f"empty", data=None, fitting_method=[0, 0, 0, 0, 0],
            datetime=new_blank_sequence['experimentTime'], type_str='blank', is_estimated=True,
            results=[
                new_blank_sequence['Ar36'],
                new_blank_sequence['Ar37'],
                new_blank_sequence['Ar38'],
                new_blank_sequence['Ar39'],
                new_blank_sequence['Ar40'],
            ],
        )

        raw.sequence.append(new_sequence)
        http_funcs.create_cache(raw, cache_key=self.cache_key)  # update raw

        return JsonResponse({'new_sequence': new_sequence},
                            encoder=ap.smp.json.MyEncoder, content_type='application/json', safe=True)

    def change_seq_fitting_method(self, request, *args, **kwargs):
        raw: ap.RawData = self.sample
        seq_idx = self.body['sequence_index']
        iso_idx = self.body['isotope_index']
        fit_idx = self.body['fitting_index']
        # print(f"{seq_idx = }, {iso_idx = }, {fit_idx = }")
        raw.get_sequence(seq_idx).fitting_method[iso_idx] = fit_idx
        http_funcs.create_cache(raw, cache_key=self.cache_key)  # update raw
        return JsonResponse({})

    def change_seq_state(self, request, *args, **kwargs):
        raw: ap.RawData = self.sample
        seq_idx = self.body['sequence_index']
        is_blank = self.body['is_blank']
        is_removed = self.body['is_removed']
        seq = raw.get_sequence(seq_idx)
        seq.as_type(is_blank and "blank")
        seq.is_removed = is_removed
        http_funcs.create_cache(raw, cache_key=self.cache_key)  # update raw
        return JsonResponse({})

    def to_project_view(self, request, *args, **kwargs):
        log_funcs.set_info_log(self.ip, '004', 'info', f'Upload raw project')
        return http_funcs.open_last_object(request)
        # return redirect('object_views_2')

    def calc_raw_chart_clicked(self, request, *args, **kwargs):

        selectionForAll = self.body['selectionForAll']
        sequence_index = self.body['sequence_index']
        data_index = self.body['data_index']
        isotopic_index = self.body['isotopic_index']

        raw: ap.RawData = self.sample

        status = not raw.sequence[sequence_index].flag[data_index][isotopic_index * 2 + 1]
        isotopic_index = list(range(5)) if selectionForAll else [isotopic_index]

        for _isotope in isotopic_index:
            raw.sequence[sequence_index].flag[data_index][_isotope * 2 + 1] = status
            raw.sequence[sequence_index].flag[data_index][_isotope * 2 + 2] = status

        raw.do_regression(sequence_index=[sequence_index], isotopic_index=isotopic_index)

        http_funcs.create_cache(raw, cache_key=self.cache_key)  # update raw data in cache

        return JsonResponse({'sequence': raw.sequence[sequence_index]},
                            encoder=ap.smp.json.MyEncoder, content_type='application/json', safe=True)

    def calc_raw_average_blanks(self, request, *args, **kwargs):
        blanks = self.body['blanks']
        log_funcs.set_info_log(
            self.ip, '004', 'info',
            f'Calculate average value of selected blanks, '
            f'the number of selected points will be lesser than 4')
        newBlank = []
        results = []
        for i in range(5):
            _intercept = sum([j[i]['intercept'] for j in blanks]) / len(blanks)
            _err = ap.calc.err.div(
                (_intercept, ap.calc.err.add(*[j[i]['absolute err'] for j in blanks])), (len(blanks), 0))
            _relative_err = _err / _intercept * 100
            isotope = {
                'isotope': ["Ar36", "Ar37", "Ar38", "Ar39", "Ar40"][i],
                'intercept': _intercept, 'absolute err': _err, 'relative err': _relative_err, 'r2': None, 'mswd': None
            }
            newBlank.append(isotope)
            results.append([[_intercept, _err, _relative_err, np.nan]])
        new_sequence = ap.Sequence(
            index='undefined', name=f"average({', '.join([j[0]['name'] for j in blanks])})", data=None,
            datetime='', type_str='blank', results=results, fitting_method=[0, 0, 0, 0, 0], is_estimated=True,
        )

        raw: ap.RawData = self.sample
        raw.sequence.append(new_sequence)
        http_funcs.create_cache(raw, cache_key=self.cache_key)

        return JsonResponse({'newBlank': newBlank, 'new_sequence': new_sequence},
                            encoder=ap.smp.json.MyEncoder, content_type='application/json', safe=True)

    def calc_raw_interpolated_blanks(self, request, *args, **kwargs):
        """
        Parameters
        ----------
        request
        args
        kwargs

        Returns
        -------

        """

        interpolated_blank = self.body['interpolated_blank']
        raw: ap.RawData = self.sample
        new_sequences = [ap.Sequence(
            name="Interpolated Blank", results=[[[iso[1], 0, np.NaN, np.NaN]] for iso in row],
            fitting_method=[0, 0, 0, 0, 0], index=index, datetime=row[0][0], type_str='blank',
            is_estimated=True,
        ) for index, row in enumerate(interpolated_blank)]
        raw.interpolated_blank = new_sequences

        http_funcs.create_cache(raw, cache_key=self.cache_key)  # update cache

        return JsonResponse({'sequences': new_sequences},
                            encoder=ap.smp.json.MyEncoder, content_type='application/json', safe=True)

    def raw_data_submit(self, request, *args, **kwargs):
        """
        Raw data submit, return a sample instance and render a object html.
        """
        irradiationParams = self.body['irradiationParams']
        calculationParams = self.body['calculationParams']
        sampleParams = self.body['sampleParams']
        sampleInfo = self.body['sampleInfo']
        selectedSequences = self.body['selectedSequences']
        fingerprint = self.body['fingerprint']
        log_funcs.set_info_log(self.ip, '004', 'info', f'Start to submit raw file')

        raw: ap.RawData = self.sample

        # create sample
        sample = raw.to_sample(selectedSequences)

        info = {
            'sample': {'name': sampleInfo[0], 'type': sampleInfo[1], 'material': sampleInfo[2], 'location': sampleInfo[3]},
            'researcher': {'name': sampleInfo[4]},
            'laboratory': {'name': sampleInfo[5], 'info': sampleInfo[6], 'analyst': sampleInfo[7]}
        }
        sample.set_info(info=info)

        try:
            sample.set_params(irradiationParams['param'], 'irra')
            sample.set_params(calculationParams['param'], 'calc')
            sample.set_params(sampleParams['param'], 'smp')
        except (BaseException, Exception):
            print(traceback.format_exc())
        try:
            sample.recalculate(*[True] * 11, False, *[True] * 4)  # Calculation after submitting row data
            # ap.recalculate(sample, *[True] * 12)  # Calculation after submitting row data
            ap.smp.table.update_table_data(sample)  # Update table after submission row data and calculation
        except ValueError:
            return JsonResponse({'msg': traceback.format_exc()}, status=403)
        # update cache
        cache_key = http_funcs.create_cache(sample)
        # write mysql
        http_funcs.set_mysql(request, models.CalcRecord, fingerprint, cache_key=cache_key)
        log_funcs.set_info_log(self.ip, '004', 'info', f'Success to submit raw file')
        return JsonResponse({})

    def check_regression(self, request, *args, **kwargs):
        raw: ap.RawData = self.sample

        failed = []
        for seq in raw.sequence:
            if seq.is_removed:
                continue
            for ar in range(5):
                regression_res = seq.results[ar][seq.fitting_method[ar]]
                if not all([isinstance(i, (float, int)) for i in regression_res]):
                    failed.append([seq.index, seq.name, f"Ar{36+ar}"])

        msg = "All sequence are valid for later calculation!"
        if failed:
            failed = sorted(list(set([seq[0]+1 for seq in failed])))
            msg = f"Errors: {failed}"

        return JsonResponse({'status': 'successful', 'msg': msg, 'failed': failed}, status=200)

    def export_sequence(self, request, *args, **kwargs):
        """
        Parameters
        ----------
        request
        args
        kwargs

        Returns
        -------

        """
        raw: ap.RawData = self.sample
        selected = self.body['selected']
        is_blank = self.body['is_blank']
        fitting_method = self.body['fitting_method']

        def _update_sequence(_seq, _is_blank, _fitting_method):
            if _is_blank:
                _seq.type_str = "blank"
            _seq.fitting_method = _fitting_method
            return _seq

        sequences = [_update_sequence(raw.sequence[index], is_blank[index], fitting_method[index])
                     for index, is_selected in enumerate(selected) if is_selected]
        file_path = os.path.join(settings.DOWNLOAD_ROOT,
                                 f"{sequences[0].name}{' et al' if len(sequences) > 1 else ''}.seq")
        export_href = '/' + settings.DOWNLOAD_URL + f"{sequences[0].name}{' et al' if len(sequences) > 1 else ''}.seq"
        # with open(file_path, 'w') as f:  # save serialized json data to a readable text
        #     f.write(ap.smp.json.dumps(sequences))
        with open(file_path, 'wb') as f:  # save serialized json data to a readable text
            f.write(pickle.dumps(sequences))
        return JsonResponse({"href": export_href})


class ParamsSettingView(http_funcs.ArArView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatch_post_method_name = [
            "show_irra", "show_calc"
        ]

    def show_irra(self, request, *args, **kwargs):
        names = list(models.IrraParams.objects.values_list('name', flat=True))
        log_funcs.set_info_log(self.ip, '005', 'info', f'Show irradiation param project names: {names}')
        return render(request, 'irradiation_setting.html', {'allIrraNames': names})

    def show_calc(self, request, *args, **kwargs):
        names = list(models.CalcParams.objects.values_list('name', flat=True))
        log_funcs.set_info_log(self.ip, '005', 'info', f'Show calculation param project names: {names}')
        return render(request, 'calculation_setting.html', {'allCalcNames': names})

    def show_smp(self, request, *args, **kwargs):
        names = list(models.SmpParams.objects.values_list('name', flat=True))
        log_funcs.set_info_log(self.ip, '005', 'info', f'Show sample param project names: {names}')
        return render(request, 'sample_setting.html', {'allSmpNames': names})

    def show_input_filter(self, request, *args, **kwargs):
        names = list(models.InputFilterParams.objects.values_list('name', flat=True))
        log_funcs.set_info_log(self.ip, '005', 'info', f'Show input filter project names: {names}')
        return render(request, 'input_filter_setting.html', {'allInputFilterNames': names})

    # def show_export_pdf(self, request, *args, **kwargs):
    #     names = list(models.ExportPDFParams.objects.values_list('name', flat=True))
    #     log_funcs.set_info_log(self.ip, '005', 'info', f'Show export PDF project names: {names}')
    #     return render(request, 'export_pdf_setting.html', {'allExportPDFNames': names})

    def change_param_objects(self, request, *args, **kwargs):
        type = str(self.body['type'])  # type = irra, calc, smp
        model_name = f"{''.join([i.capitalize() for i in type.split('-')])}Params"
        try:
            name = self.body['name']
            param_file = getattr(models, model_name).objects.get(name=name).file_path
            param = ap.files.basic.read(param_file)
            return JsonResponse({'status': 'success', 'param': param})
        except KeyError:
            sample = self.sample
            param = []
            try:
                data = ap.calc.arr.transpose(sample.TotalParam)[0]
                if 'irra' in type.lower():
                    param = [*data[0:20], *data[56:58], *data[20:27],
                             *ap.calc.corr.get_irradiation_datetime_by_string(data[27]), data[28], '', '']
                if 'calc' in type.lower():
                    param = [*data[34:56], *data[71:97]]
                if 'smp' in type.lower():
                    _ = [i == {'l': 0, 'e': 1, 'p': 2}.get(str(data[100]).lower()[0], -1) for i in range(3)]
                    param = [*data[67:71], *data[58:67], *data[97:100], *data[115:120], *data[126:136],
                             *data[120:123], *_, *data[101:114]]
                # if 'thermo' in type.lower():
                #     param = [*data[0:20], *data[56:58], *data[20:27],
                #              *ap.calc.corr.get_irradiation_datetime_by_string(data[27]), data[28], '', '']
                if 'export' in type.lower():
                    param = [True]
            except IndexError:
                param = []
            return JsonResponse({'status': 'success', 'param': np.nan_to_num(param).tolist()})
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({'status': 'fail', 'msg': 'no param project exists in database\n' + str(e)}, status=403)

    def edit_param_object(self, request, *args, **kwargs):
        ip = http_funcs.get_ip(request)
        flag = str(self.body['flag']).lower()
        name = self.body['name']
        pin = self.body['pin']
        params = self.body['params']
        type = str(self.body['type'])  # type = irra, calc, smp, input-filter
        model_name = f"{''.join([i.capitalize() for i in type.split('-')])}Params"
        model = getattr(models, model_name)
        if flag == 'create':
            email = self.body['email']
            if name == '' or pin == '':
                log_funcs.set_info_log(
                    self.ip, '005', 'info', f'Fail to create {type.lower()} project, empty name or pin')
                return JsonResponse({'msg': 'empty name or pin'}, status=403)
            elif model.objects.filter(name=name).exists():
                log_funcs.set_info_log(
                    self.ip, '005', 'info', f'Fail to create {type.lower()} project, duplicate name, name: {name}')
                return JsonResponse({'msg': 'duplicate name'}, status=403)
            else:
                path = ap.files.basic.write(os.path.join(settings.SETTINGS_ROOT, f"{name}.{type}"), params)
                model.objects.create(name=name, pin=pin, file_path=path, uploader_email=email, ip=ip)
                log_funcs.set_info_log(
                    self.ip, '005', 'info',
                    f'Success to create {type.lower()} project, '
                    f'name: {name}, email: {email}, file path: {path}')
                return JsonResponse({'status': 'success'})
        else:
            try:
                old = model.objects.get(name=name)
            except (BaseException, Exception):
                print(traceback.format_exc())
                log_funcs.set_info_log(
                    self.ip, '005', 'info',
                    f'Fail to change selected {type.lower()} project, '
                    f'it does not exist in the server, name: {name}')
                return JsonResponse({'msg': 'current project does not exist'}, status=403)
            if pin == old.pin:
                if flag == 'update':
                    path = ap.files.basic.write(old.file_path, params)
                    old.save()
                    log_funcs.set_info_log(
                        self.ip, '005', 'info',
                        f'Success to update the {type.lower()} project, name: {name}, path: {path}')
                    return JsonResponse({'status': 'success'})
                elif flag == 'delete':
                    if ap.files.basic.delete(old.file_path):
                        old.delete()
                        log_funcs.set_info_log(
                            self.ip, '005', 'info',
                            f'Success to delete the {type.lower()} project does been deleted, name: {name}')
                        return JsonResponse({'status': 'success'})
                    else:
                        log_funcs.set_info_log(
                            self.ip, '005', 'info',
                            f'Fail to delete {type.lower()} projects, '
                            f'something wrong happened, name: {name}')
                        return JsonResponse({'msg': 'something wrong happened when delete params'}, status=403)
            else:
                return JsonResponse({'msg': 'wrong pin'}, status=403)


class ThermoView(http_funcs.ArArView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatch_post_method_name = []

    # /calc/thermo
    def get(self, request, *args, **kwargs):
        # names = list(models.IrraParams.objects.values_list('name', flat=True))
        # log_funcs.set_info_log(self.ip, '005', 'info', f'Show irradiation param project names: {names}')
        allThermoNames = list(models.ThermoParams.objects.values_list('name', flat=True))
        return render(request, 'thermo.html', {'allThermoNames': allThermoNames})

    # /calc/thermo/arr_input
    def arr_input(self, request, *args, **kwargs):
        random_index = request.POST.get('random_index')
        arr_file = request.POST.get('arr_file_name')
        heating_log_file = request.POST.get('heating_log_file_name')
        smp_name = request.POST.get('sample_name')
        suffix = ''
        destination_folder, random_index = ap.smp.diffusion_funcs.get_random_dir(
            settings.MDD_ROOT, length=7, random_index=random_index)
        for i in range(len(request.FILES)):
            try:
                file = request.FILES.get(str(i))
                web_file_path, file_name, suffix = ap.files.basic.upload(file, destination_folder)
            except (Exception, BaseException) as e:
                pass
            else:
                if str(suffix).lower() == ".arr":
                    arr_file = file_name + suffix
                    sample = ap.from_arr(file_path=web_file_path)
                    smp_name = sample.name()
                elif suffix != "":
                    heating_log_file = file_name + suffix

        return JsonResponse({"sample_name": smp_name, "arr_file": arr_file, "heating_log_file": heating_log_file,
                             "random_index": random_index, "suffix": suffix})

    # /calc/thermo/check_sample
    def check_sample(self, request, *args, **kwargs):
        # names = list(models.IrraParams.objects.values_list('name', flat=True))
        # log_funcs.set_info_log(self.ip, '005', 'info', f'Show irradiation param project names: {names}')

        name = self.body['name']
        arr_file_name = self.body['arr_file_name']
        random_index = self.body['random_index']
        params = self.body['settings']

        loc = os.path.join(settings.MDD_ROOT, f'{random_index}')
        if not os.path.exists(loc) or random_index == "":
            return JsonResponse({}, status=403)

        mch_out = os.path.join(loc, f'{arr_file_name}_mch-out.dat')
        mages_out = os.path.join(loc, f'{arr_file_name}_mages-out.dat')
        ages_sd = os.path.join(loc, f'{arr_file_name}_ages-sd.samp')
        file_path = os.path.join(loc, f"{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))

        sample = ap.from_arr(file_path=file_path)
        sequence = sample.sequence()
        nsteps = sequence.size
        te = np.array(sample.TotalParam[124], dtype=np.float64)
        ti = (np.array(sample.TotalParam[123], dtype=np.float64) / 60).round(2)  # time in minute
        nindex = {"40": 24, "39": 20, "38": 10, "37": 8, "36": 0}
        if params[10] in list(nindex.keys()):
            ar = np.array(sample.DegasValues[nindex[params[10]]], dtype=np.float64)  # 20-21 Ar39
            sar = np.array(sample.DegasValues[nindex[params[10]] + 1], dtype=np.float64)
        elif params[10] == 'total':
            all_ar = np.array(sample.CorrectedValues, dtype=np.float64)  # 20-21 Ar39
            ar, sar = ap.calc.arr.add(*all_ar.reshape(5, 2, len(all_ar[0])))
            ar = np.array(ar); sar = np.array(sar)
        else:
            raise KeyError
        age = np.array(sample.ApparentAgeValues[2], dtype=np.float64)  # 2-3 age
        sage = np.array(sample.ApparentAgeValues[3], dtype=np.float64)
        f = np.cumsum(ar) / ar.sum()

        # dr2, ln_dr2 = ap.smp.diffusion_funcs.dr2_popov(f, ti)
        ln = True if str(params[6]).lower() == 'ln' else False
        if str(params[7]).lower() == 'lovera':
            dr2, ln_dr2, wt = ap.smp.diffusion_funcs.dr2_lovera(f, ti, ar=ar, sar=sar, ln=ln)
        elif str(params[7]).lower() == 'yang':
            dr2, ln_dr2, wt = ap.smp.diffusion_funcs.dr2_yang(f, ti, ar=ar, sar=sar, ln=ln)
        elif str(params[7]).lower() == 'popov':
            dr2, ln_dr2, wt = ap.smp.diffusion_funcs.dr2_popov(f, ti, ar=ar, sar=sar, ln=ln)
        else:
            return JsonResponse({}, status=403)

        data = np.array([
            sequence.value, te, ti, age, sage, ar, sar, f, dr2, ln_dr2, wt
        ]).tolist()
        data.insert(0, (np.where(np.array(data[3]) > 0, True, False) & np.isfinite(data[3])).tolist())
        data.insert(1, [1 for i in range(nsteps)])

        res = False
        if os.path.isfile(mch_out) and os.path.isfile(mages_out) and os.path.isfile(ages_sd):
            res = True

        return JsonResponse({'status': 'success', 'has_files': res, 'data': ap.smp.json.dumps(data)})


    def run_arrmulti(self, request, *args, **kwargs):
        sample_name = self.body['sample_name']
        arr_file_name = self.body['arr_file_name']
        random_index = self.body['random_index']
        max_age = self.body['max_age']
        data = self.body['data']
        params = self.body['settings']

        print(data)

        loc = os.path.join(settings.MDD_ROOT, f'{random_index}')
        if not os.path.exists(loc) or random_index == "":
            return JsonResponse({"random_index": random_index}, status=403)

        file_path = os.path.join(loc, f"{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))
        sample = ap.from_arr(file_path=file_path)

        arr = ap.smp.diffusion_funcs.DiffArrmultiFunc(smp=sample, loc=loc)

        print(f"{params = }")
        # params = [8, 10, 8, 2, 0.5, 0.01, 'wt', 'xlogd', 'random', 'fit', False]
        filtered_data = list(filter(lambda x: x[0], data))
        filtered_index = [i for i, row in enumerate(data) if row[0]]
        arr.ni = len(filtered_data)
        data = ap.calc.arr.transpose(data)
        filtered_data = ap.calc.arr.transpose(filtered_data)
        arr.telab = [i + 273.15 for i in filtered_data[3]]
        arr.tilab = [i * 60 for i in filtered_data[4]]
        arr.ya = filtered_data[5]
        arr.sig = filtered_data[6]
        arr.a39 = filtered_data[7]
        arr.sig39 = filtered_data[8]
        arr.f = filtered_data[9]
        # dr2, arr.xlogd, arr.wt = ap.smp.diffusion_funcs.dr2_lovera(
        #     f=arr.f, ti=filtered_data[4], ar=filtered_data[7], sar=filtered_data[8], ln=False)
        dr2, arr.xlogd, arr.wt = filtered_data[10:13]

        arr.f.insert(0, 0)
        arr.f = np.where(np.array(arr.f) >= 1, 0.9999999999999999, np.array(arr.f))
        arr.main()

        return JsonResponse({})


    def run_agemon(self, request, *args, **kwargs):
        sample_name = self.body['sample_name']
        arr_file_name = self.body['arr_file_name']
        random_index = self.body['random_index']
        max_age = self.body['max_age']
        data = self.body['data']
        loc = os.path.join(settings.MDD_ROOT, random_index)
        if not os.path.exists(loc) or random_index == "":
            return JsonResponse({}, status=403)

        file_path = os.path.join(loc, f"{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))
        sample = ap.from_arr(file_path=file_path)

        sample.name(arr_file_name)

        use_dll = True
        # use_dll = False

        data = list(filter(lambda x: x[0], data))

        if use_dll:
            if os.name == 'nt':  # Windows system
                source = os.path.join(settings.SETTINGS_ROOT, "mddfuncs.dll")
            elif os.name == 'posix':  # Linux
                source = os.path.join(settings.SETTINGS_ROOT, "mddfuncs.so")
            else:
                return JsonResponse({}, status=403)
            ap.smp.diffusion_funcs.run_agemon_dll(sample, source, loc, data, float(max_age))
        else:
            agemon = ap.smp.diffusion_funcs.DiffAgemonFuncs(smp=sample, loc=loc)

            agemon.max_plateau_age = float(max_age)
            agemon.ni = len(data)
            agemon.nit = agemon.ni
            data = ap.calc.arr.transpose(data)
            agemon.r39 = np.zeros(agemon.nit + 1, dtype=np.float64)
            agemon.telab = np.zeros(100, dtype=np.float64)
            agemon.tilab = np.zeros(100, dtype=np.float64)
            agemon.ya = np.zeros(100, dtype=np.float64)
            agemon.sig = np.zeros(100, dtype=np.float64)
            agemon.a39 = np.zeros(100, dtype=np.float64)
            agemon.sig39 = np.zeros(100, dtype=np.float64)
            agemon.xs = np.zeros(100, dtype=np.float64)

            for i in range(agemon.nit):
                agemon.ya[i + 1] = data[5][i]
                agemon.sig[i] = data[6][i]
                agemon.a39[i] = data[7][i]
                agemon.sig39[i] = data[8][i]
                agemon.xs[i + 1] = data[9][i]
                agemon.telab[i] = data[3][i] + 273.15
                agemon.tilab[i] = data[4][i] / 5.256E+11

            agemon.xs = np.where(np.array(agemon.xs) >= 1, 0.9999999999999999, np.array(agemon.xs))

            for i in range(agemon.nit):
                if agemon.telab[i] > 1373:
                    agemon.ni = i
                    break

            agemon.main()



        return JsonResponse({})


    def run_walker(self, request, *args, **kwargs):
        sample_name = self.body['sample_name']
        arr_file_name = self.body['arr_file_name']
        random_index = self.body['random_index']
        max_age = self.body['max_age']
        data = self.body['data']
        params = self.body['settings']
        loc = os.path.join(settings.MDD_ROOT, f'{random_index}')
        if not os.path.exists(loc) or random_index == "":
            return JsonResponse({"random_index": random_index}, status=403)
        arr_file_path = os.path.join(loc, f"{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))

        # setting_params = params[:11]
        domain_params = params[11:32]
        # plot_params = params[32:]

        # 活化能和体积比例从外到内
        energies = (np.array(domain_params[0:16:2]) * 1000).tolist()
        fractions = domain_params[1:16:2]
        ndoms = len(energies)
        use_walker1 = domain_params[16] == "walker1"
        k = domain_params[17]
        gs = domain_params[18]
        # ad = domain_params[19]  # atom density
        # f = domain_params[20]  # frequency
        ad = 1e10  # atom density
        f = 1e13

        print(f"{use_walker1 = }, {k = }, {gs = }, {ad = }, {f = }")

        smp = ap.from_arr(arr_file_path)
        ti = np.array(smp.TotalParam[123], dtype=np.float64).round(2)  # time in second
        times = np.cumsum(ti)  # cumulative time
        temps = np.array(smp.TotalParam[124], dtype=np.float64)  # temperature in Celsius
        ar = np.array(smp.DegasValues[20], dtype=np.float64)  # Ar39K
        target = ar.cumsum() / sum(ar)

        file_name = f"{'walker1' if use_walker1 else 'walker2'} {k=:.1f} " \
                    f"es={'-'.join([str(int(i/1000)) for i in energies])} " \
                    f"fs={'-'.join([str(i) for i in fractions])} multi"

        try:
            demo, status = ap.ads.main.run(
                times, temps, energies, fractions, ndoms, file_name=file_name, k=k, grain_szie=gs,
                atom_density=ad, frequency=f, simulation=False, target=target, epsilon=0.05, use_walker1=use_walker1
            )
        except ap.ads.main.OverEpsilonError as e:
            return JsonResponse({})
        else:
            ap.ads.main.save_ads(demo, f"{loc}", name=demo.name)

        return JsonResponse({})


    def plot(self, request, *args, **kwargs):
        # names = list(models.IrraParams.objects.values_list('name', flat=True))
        # log_funcs.set_info_log(self.ip, '005', 'info', f'Show irradiation param project names: {names}')
        sample_name = self.body['sample_name']
        arr_file_name = self.body['arr_file_name']
        heating_log = self.body['heating_log_file_name']
        random_index = self.body['random_index']
        data = self.body['data']
        params = self.body['settings']

        loc = os.path.join(settings.MDD_ROOT, f'{random_index}')
        if not os.path.exists(loc) or random_index == "":
            return JsonResponse({}, status=403)

        n = len(data)
        data = ap.calc.arr.transpose(data)

        # read_from_ins = True
        read_from_ins = False

        plot_params = params[33:]

        line_data = [a, b, siga, sigb, chi2, q] = [0, 0, 0, 0, 0, 0]
        if plot_params[0]:  # arrhenius plot
            ti = [i + 273.15 for i in data[3]]
            x, y, wtx, wty = [], [], [], []
            for i in range(len(ti)):
                if str(data[1][i]) == "2":
                    x.append(10000 / ti[i])
                    wtx.append(10000 * 5 / ti[i] ** 2)
                    y.append(data[11][i])
                    wty.append(data[12][i])
            if len(x) > 0:
                try:
                    line_data = [a, b, siga, sigb, chi2, q] = ap.smp.diffusion_funcs.fit(x, y, wtx, wty)
                except:
                    pass

        if all(plot_params[1:3]):  # Age spectra and cooling history
            if read_from_ins:
                mdd_loc = r"C:\Users\Young\OneDrive\00-Projects\【2】个人项目\2024-06 MDD\MDDprograms\Sources Codes"
                arr = ap.smp.diffusion_funcs.DiffDraw(name="Y51a", loc=mdd_loc, read_from_ins=read_from_ins)
            else:
                file_path = os.path.join(loc, f"{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))
                sample = ap.from_arr(file_path=file_path)

                arr = ap.smp.diffusion_funcs.DiffDraw(smp=sample, loc=loc)
                arr.ni = n
                arr.telab = [i + 273.15 for i in data[3]]
                arr.tilab = [i * 60 for i in data[4]]
                arr.age = data[5]
                arr.sage = data[6]
                arr.a39 = data[7]
                arr.sig39 = data[8]
                arr.f = data[9]
            plot_data = list(arr.get_plot_data())
        else:
            plot_data = [[], [], [], []]

        furnace_log = []
        heating_out = []
        if plot_params[3]:  # heating log
            try:
                furnace_log = libano_log = np.loadtxt(os.path.join(loc, f"{heating_log}"), delimiter=',')
                # heating_out = np.loadtxt(os.path.join(loc, f"{file_name}-heated-index.txt"), delimiter=',', dtype=int)
                # heating_out = np.loadtxt(os.path.join(loc, f"{file_name}-heated-index.txt"), delimiter=',', dtype=int)
            except FileNotFoundError:
                print(f"FileNotFoundError")
                furnace_log = [[], [], [], [], [], []]
                heating_out = []
            else:
                # passs
                # heating_timestamp = [j for v in heating_out for j in libano_log[0, v]]  # 加热起止点的时间标签
                # furnace_log = [libano_log[:, 0]]
                # for i in range(1, libano_log.shape[1] - 1):
                #     if not all([(i==i[0]).all() for i in libano_log[[1, 2, 4, 5], i-1: i+2]]) or libano_log[0, i] in heating_timestamp:
                #         furnace_log.append(libano_log[:, i])
                # furnace_log.append(libano_log[:, -1])
                # furnace_log = np.transpose(furnace_log)
                # heating_out = np.reshape([index for index, _ in enumerate(furnace_log[0]) if _ in heating_timestamp], (len(heating_timestamp) // 2, 2))
                pass
        plot_data.append(furnace_log)
        plot_data.append(heating_out)

        released = []
        release_name = []
        if plot_params[4]:  # release pattern
            ar = data[7]
            ads_released = []
            index = 1
            for (dirpath, dirnames, fs) in os.walk(loc):
                for f in fs:
                    if f.endswith(".ads"):
                        if not os.path.exists(os.path.join(loc, f)):
                            continue
                        index += 1
                        release_name.append(f"Released{index}: {f}")
                        diff = ap.ads.main.read_ads(os.path.join(loc, f))
                        ads_released.append(np.array(diff.released_per_step) / diff.natoms)

            ads_released = np.transpose(ads_released)

            for i in range(len(ads_released)):
                released.append([i+1, sum(ar[0:i+1]) / sum(ar), *ads_released[i]])
        else:
            released.append([])
        plot_data.append(released)
        release_name = '\n'.join(release_name)

        return JsonResponse({'status': 'success', 'data': ap.smp.json.dumps(plot_data),
                             'line_data': ap.smp.json.dumps(line_data), 'release_name': release_name})


    def read_log(self, request, *args, **kwargs):
        sample_name = self.body['sample_name']
        arr_file_name = self.body['arr_file_name']
        loc = f"C:\\Users\\Young\\OneDrive\\00-Projects\\【2】个人项目\\2022-05论文课题\\【3】分析测试\\ArAr\\01-VU实验数据和记录\\{sample_name}"

        libano_log_path = f"{loc}\\Libano-log"
        libano_log_path = [os.path.join(libano_log_path, i) for i in os.listdir(libano_log_path)]
        helix_log_path = f"{loc}\\LogFiles"
        helix_log_path = [os.path.join(helix_log_path, i) for i in os.listdir(helix_log_path)]

        ap.smp.diffusion_funcs.SmpTemperatureCalibration(
            libano_log_path=libano_log_path, helix_log_path=helix_log_path, loc=loc, name=arr_file_name)

        return JsonResponse({})


class ExportView(http_funcs.ArArView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatch_post_method_name = []

    # /calc/export
    def get(self, request, *args, **kwargs):
        names = list(models.ExportPdfParams.objects.values_list('name', flat=True))
        return render(request, 'export_pdf_setting.html', {'allExportPDFNames': names})

    def get_plotdata(self, request, *args, **kwargs):
        params = self.body['settings']
        files = json.loads(self.body['json_string'])['files']
        file_names = [each['file_name'] for each in files if each['checked']]
        file_paths = [each['file_path'] for each in files if each['checked']]
        diagrams = [each['diagram'] for each in files if each['checked']]
        print(f"{file_names = }")
        print(f"{file_paths = }")
        print(f"{diagrams = }")
        print(f"{params = }")

        colors = [
            '#1f3c40', '#e35000', '#e1ae0f', '#3d8ebf', '#77dd83', '#c7ae88', '#83d6bb', '#653013', '#cc5f16',
            '#d0b269',
            '#002b5b', '#d7263d', '#3a9679', '#f49d1a', '#523e6a', '#97a7b3', '#ff6f61', '#2a9d8f', '#e63946',
            '#264653',
            '#ffe156', '#6a0572', '#e6399b', '#255f85', '#47e5bc', '#ff924c', '#1b1f3b', '#d7c9aa', '#935116', '#495867'
        ]

        # ------ 构建数据 -------
        data = {"data": [], "file_name": "WebArAr"}
        smps = []
        for index, file in enumerate(file_paths):
            _, ext = os.path.splitext(file)
            if ext[1:] not in ['arr', 'age']:
                continue
            smps.append((ap.from_arr if ext[1:] == 'arr' else ap.from_age)(file_path=file))

        keys = [
            "page_size", "ppi", "width", "height", "pt_width", "pt_height", "pt_left", "pt_bottom",
            "offset_top", "offset_right", "offset_bottom", "offset_left", "plot_together", "show_frame",
        ]
        params = dict(zip(keys, [int(val) if str(val).isnumeric() else val for val in params]))
        plot_together = params.get("plot_together", True)

        if params.get("plot_together", True):
            data['data'] = [{"name": "", "xAxis": [], "yAxis": [], "series": []}]
        for index, smp in enumerate(smps):
            if plot_together:
                current = ap.smp.export.get_plot_data(smp=smp, diagram=diagrams[index], color=colors[index])
                data['data'][0]['name'] = 'Combined Diagrams'
                if index == 0:
                    data['data'][0]['xAxis'] = current['xAxis']
                    data['data'][0]['yAxis'] = current['yAxis']
                else:
                    data['data'][0]['xAxis'][0]['extent'][0] = min(current['xAxis'][0]['extent'][0], data['data'][0]['xAxis'][0]['extent'][0])
                    data['data'][0]['xAxis'][0]['extent'][1] = max(current['xAxis'][0]['extent'][1], data['data'][0]['xAxis'][0]['extent'][1])
                    data['data'][0]['yAxis'][0]['extent'][0] = min(current['yAxis'][0]['extent'][0], data['data'][0]['yAxis'][0]['extent'][0])
                    data['data'][0]['yAxis'][0]['extent'][1] = max(current['yAxis'][0]['extent'][1], data['data'][0]['yAxis'][0]['extent'][1])
                for ser in current['series']:
                    data['data'][0]['series'].append(ser)
            else:
                current = ap.smp.export.get_plot_data(smp=smp, diagram=diagrams[index])
                data['data'].append(current)

        filepath = f"{settings.DOWNLOAD_URL}{data['file_name']}-{uuid.uuid4().hex[:8]}.pdf"
        filepath = ap.smp.export.export_chart_to_pdf(data, filepath=filepath, **params)
        export_href = '/' + filepath

        return JsonResponse({'data': ap.smp.json.dumps(data), 'href': export_href})


class ApiView(http_funcs.ArArView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatch_post_method_name = [
        ]

    @staticmethod
    def open_raw(request, *args, **kwargs):
        return CalcHtmlView().open_raw_file(request, *args, **kwargs)

    @staticmethod
    def open_arr(request, *args, **kwargs):
        return CalcHtmlView().open_arr_file(request, *args, **kwargs)

    @staticmethod
    def open_full(request, *args, **kwargs):
        return CalcHtmlView().open_full_xls_file(request, *args, **kwargs)

    @staticmethod
    def open_age(request, *args, **kwargs):
        return CalcHtmlView().open_age_file(request, *args, **kwargs)

    @staticmethod
    def open_current(request, *args, **kwargs):
        return CalcHtmlView().open_current_file(request, *args, **kwargs)

    @staticmethod
    def open_new(request, *args, **kwargs):
        return CalcHtmlView().open_new_file(request, *args, **kwargs)

    @staticmethod
    def open_multi(request, *args, **kwargs):
        return CalcHtmlView().open_multi_files(request, *args, **kwargs)

    @staticmethod
    def multi_files(request, *args, **kwargs):
        res = []
        try:
            length = int(request.POST.get('length'))
        except TypeError:
            files = request.FILES.getlist('files')
        else:
            files = [request.FILES.get(str(i)) for i in range(length)]
        print(f"Number of files: {len(files)}")
        for file in files:
            try:
                web_file_path, file_name, suffix = ap.files.basic.upload(
                    file, settings.UPLOAD_ROOT)
            except (Exception, BaseException):
                continue
            else:
                res.append({
                    'name': file_name, 'extension': suffix, 'path': web_file_path,
                })
        return JsonResponse({'files': res})

    def export_arr(self, request, *args, **kwargs):
        sample = self.sample
        print(self.sample.Info.results.isochron['figure_2'])
        export_name = ap.files.arr_file.save(settings.DOWNLOAD_ROOT, sample)
        export_href = '/' + settings.DOWNLOAD_URL + export_name
        log_funcs.set_info_log(self.ip, '003', 'info',
                               f'Success to export webarar file (.arr), sample name: {sample.Info.sample.name}, '
                               f'export href: {export_href}')
        return JsonResponse({'status': 'success', 'href': export_href})

    def export_xls(self, request, *args, **kwargs):
        template_filepath = os.path.join(settings.SETTINGS_ROOT, 'excel_export_template.xlstemp')
        export_filepath = os.path.join(settings.DOWNLOAD_ROOT, f"{self.sample.Info.sample.name}_export.xlsx")
        default_style = {
            'font_size': 10, 'font_name': 'Microsoft Sans Serif', 'bold': False,
            'bg_color': '#FFFFFF',  # back ground
            'font_color': '#000000', 'align': 'left',
            'top': 1, 'left': 1, 'right': 1, 'bottom': 1  # border width
        }
        a = ap.smp.export.WritingWorkbook(
            filepath=export_filepath, style=default_style,
            template_filepath=template_filepath, sample=self.sample)
        res = a.get_xls()
        export_href = '/' + settings.DOWNLOAD_URL + f"{self.sample.Info.sample.name}_export.xlsx"
        if res:
            log_funcs.set_info_log(
                self.ip, '003', 'info', f'Success to export excel file (.xls), '
                                        f'sample name: {self.sample.Info.sample.name}, export href: {export_href}')
            return JsonResponse({'status': 'success', 'href': export_href})
        else:
            log_funcs.set_info_log(self.ip, '003', 'info',
                                   f'Fail to export excel file (.xls), sample name: {self.sample.Info.sample.name}')
            return JsonResponse({'status': 'fail', 'msg': res})

    def export_opju(self, request, *args, **kwargs):
        name = f"{self.sample.Info.sample.name}_export"
        export_filepath = os.path.join(settings.DOWNLOAD_ROOT, f"{name}.opju")
        a = ap.smp.export.CreateOriginGraph(
            name=name, export_filepath=export_filepath, sample=self.sample,
            spectra_data=ap.calc.arr.transpose(self.sample.AgeSpectraPlot.data),
            set1_spectra_data=ap.calc.arr.transpose(self.sample.AgeSpectraPlot.set1.data),
            set2_spectra_data=ap.calc.arr.transpose(self.sample.AgeSpectraPlot.set2.data),
            isochron_data=self.sample.IsochronValues,
            isochron_lines_data=ap.calc.arr.transpose(self.sample.NorIsochronPlot.line1.data) +
                                ap.calc.arr.transpose(self.sample.NorIsochronPlot.line2.data) +
                                ap.calc.arr.transpose(self.sample.InvIsochronPlot.line1.data) +
                                ap.calc.arr.transpose(self.sample.InvIsochronPlot.line2.data) +
                                ap.calc.arr.transpose(self.sample.KClAr1IsochronPlot.line1.data) +
                                ap.calc.arr.transpose(self.sample.KClAr1IsochronPlot.line2.data) +
                                ap.calc.arr.transpose(self.sample.KClAr2IsochronPlot.line1.data) +
                                ap.calc.arr.transpose(self.sample.KClAr2IsochronPlot.line2.data) +
                                ap.calc.arr.transpose(self.sample.KClAr3IsochronPlot.line1.data) +
                                ap.calc.arr.transpose(self.sample.KClAr3IsochronPlot.line2.data),
        )
        try:
            a.get_graphs()
        except (Exception, BaseException):
            log_funcs.set_info_log(
                self.ip, '003', 'info',
                f'Fail to export origin file (.opju), sample name: {self.sample.Info.sample.name}')
            return JsonResponse({'status': 'fail', 'msg': traceback.format_exc()})
        else:
            export_href = '/' + settings.DOWNLOAD_URL + f"{name}.opju"
            log_funcs.set_info_log(self.ip, '003', 'info', f'Success to export origin file (.opju), '
                                                           f'sample name: {self.sample.Info.sample.name}, '
                                                           f'export href: {export_href}')
            return JsonResponse({'status': 'success', 'href': export_href})

    def export_pdf(self, request, *args, **kwargs):

        figure_id = str(self.body.get('figure_id'))
        merged_pdf = bool(self.body.get('merged_pdf'))
        figure = ap.smp.basic.get_component_byid(self.sample, figure_id)

        name = f"{self.sample.Info.sample.name}_{figure.name}"
        export_filepath = os.path.join(settings.DOWNLOAD_ROOT, f"{name}.pdf")

        if not merged_pdf:
            ap.smp.export.to_pdf(export_filepath, figure_id, self.sample)
        else:
            pass

        export_href = '/' + settings.DOWNLOAD_URL + f"{name}.pdf"

        return JsonResponse({'status': 'success', 'href': export_href})

        # Write clipboard
        # import win32clipboard as cp
        # cp.OpenClipboard()
        # # DataObject = 49161
        # # Object Descriptor = 49166
        # # Ole Private Data = 49171
        # # Scalable Vector Graphics = 50148
        # # Portable Document Format = 50199
        # # Scalable Vector Graphics For Adobe Muse = 50215
        # # ADOBE AI3 = 50375
        # # Adobe Illustrator 25.0 = 50376
        # # Encapsulated PostScript = 50379
        # cp.EmptyClipboard()
        # cp.SetClipboardData(cp.RegisterClipboardFormat('Portable Document Format'), pdf_data)
        # cp.CloseClipboard()

    def export_chart(self, request, *args, **kwargs):
        data = self.body['data']
        params = self.body['settings']
        keys = [
            "page_size", "ppi", "width", "height", "pt_width", "pt_height", "pt_left", "pt_bottom",
            "offset_top", "offset_right", "offset_bottom", "offset_left", "plot_together", "show_frame",
        ]
        params = dict(zip(keys, [int(val) if str(val).isnumeric() else val for val in params]))

        file_name = data.get('file_name', 'file_name')
        filepath = f"{settings.DOWNLOAD_URL}{file_name}-{uuid.uuid4().hex[:8]}.pdf"
        filepath = ap.smp.export.export_chart_to_pdf(data, filepath, **params)
        export_href = '/' + filepath

        return JsonResponse({'status': 'success', 'href': export_href})

