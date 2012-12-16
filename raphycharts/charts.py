# -*- coding: utf8 -*-

import json
import copy


def date_to_dict(date):
    return {
        'year': date.year,
        'month': date.month - 1,
        'day': date.day,
        'hour': date.hour,
        'minute': date.minute,
        'second': date.second
    }

class RaphyChart(object):

    chart_type = "generic"

    def __init__(self, chart_id="raphy-generic-chart", options={},
        width=500, height=200):
        self.chart_id = chart_id
        self.options = options
        self.width = width
        self.height = height


class LineObject(object):

    def __init__(self, data=[], options={}, x_axis_type="numeric",
        y_axis_type="numeric", tooltip_date_format="%m/%d",
        custom_tooltip=False):
        self.data = data
        self.options = options
        self.x_axis_type = x_axis_type
        self.y_axis_type = y_axis_type
        self.tooltip_date_format = tooltip_date_format
        self.custom_tooltip = custom_tooltip
        self.data_for_json = self.line_data_for_json()

    def visit_point_x(self, x):
        if self.x_axis_type == 'date':
            return date_to_dict(x)
        return x

    def visit_point_y(self, y):
        if self.y_axis_type == 'date':
            return self.date_to_dict(y)
        return y

    def get_date_tooltip(self, d):
        return d.strftime(self.tooltip_date_format)

    def tooltip_x(self, x):
        if self.x_axis_type == 'date':
            return self.get_date_tooltip(x)
        return x

    def tooltip_y(self, y):
        if self.y_axis_type == "date":
            return self.get_date_tooltip(y)
        return y

    def tooltip(self, point):
        return "%s at %s" % (self.tooltip_y(point[1]),
            self.tooltip_x(point[0])
        )

    def insert_options_into_datapoint(self, datapoint, point):
        if len(point) == 3:
            options = point[2]
        else:
            options = {}
        if 'tooltip' not in options and self.custom_tooltip:
            options['tooltip'] = self.tooltip(point)
        datapoint.append(options)

    def visit_point(self, point):
        datapoint = [self.visit_point_x(point[0]),
                        self.visit_point_y(point[1])]
        self.insert_options_into_datapoint(datapoint, point)
        return datapoint

    def line_data_for_json(self):
        data = copy.copy(self.data)
        for n, point in enumerate(data):
            data[n] = self.visit_point(point)
        return data


class RaphyLineChart(RaphyChart):

    chart_type = "linechart"
    
    def __init__(self, chart_id="raphy-linechart", options={},
        width=500, height=200,
        x_axis_type='numeric', y_axis_type='numeric',
        tooltip_date_format="%m/%d", custom_tooltip=False,
        template="raphycharts/linechart.html"):
        super(RaphyLineChart, self).__init__(chart_id, options, width=width,
            height=height)
        self.x_axis_type = x_axis_type
        self.y_axis_type = y_axis_type
        self.tooltip_date_format = tooltip_date_format
        self.custom_tooltip = custom_tooltip
        self.template = template
        self.lines = []

    def add_line(self, data=[], options={},
            tooltip_date_format=None,
            custom_tooltip=None,
            line_class=LineObject):
        self.lines.append(line_class(data, options,
            x_axis_type=self.x_axis_type, y_axis_type=self.y_axis_type,
            tooltip_date_format=tooltip_date_format or \
                self.tooltip_date_format,
            custom_tooltip=custom_tooltip or self.custom_tooltip)
        )

    def get_chart_json(self):
        return json.dumps({
            'lines': [
                {
                    'data': line.data_for_json,
                    'options': line.options,
                    'x_axis_type': self.x_axis_type,
                    'y_axis_type': self.y_axis_type
                } for line in self.lines
            ],
            'options': self.options
        })

    def render(self):
        import json
        from django import template
        from django.template import Context
        from django.template.loader import get_template
        from django.utils.safestring import mark_safe
        template_obj = get_template(self.template)
        context = Context({
            "chart_data": mark_safe(self.get_chart_json()),
            "chart_id": self.chart_id,
            'chart_width': self.width,
            'chart_height': self.height
        })
        return template_obj.render(context)