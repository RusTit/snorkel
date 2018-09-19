import pudgy
from .components import *

import backend
import dotmap
import werkzeug

def make_dict(arr):
    return dict([(w,w) for w in arr])

START_TIME_OPTIONS = [
    "-1 hour",
    "-3 hours",
    "-6 hours",
    "-12 hours",
    "-1 day",
    "-3 days",
    "-1 week",
    "-2 weeks",
    "-1 month",
    "-3 months",
    "-6 months",
    "-1 year"
]

END_TIME_OPTIONS = [
    "Now",
    "-1 hour",
    "-3 hours",
    "-6 hours",
    "-12 hours",
    "-1 day",
    "-3 days",
    "-1 week",
    "-2 weeks",
    "-1 month",
]

AGAINST_TIME_OPTIONS = [
    "",
    "-1 hour",
    "-3 hours",
    "-6 hours",
    "-12 hours",
    "-1 day",
    "-3 days",
    "-1 week",
    "-2 weeks",
]

TIME_SLICE_OPTIONS = [
    "auto",
    ("1 min", 60),
    ("5 min", 60 * 5),
    ("10 min", 60 * 10),
    ("30 min", 60 * 30),
    ("1 hour", 60 * 60),
    ("3 hours", 60 * 60 * 3),
    ("6 hours", 60 * 60 * 6),
    ("12 hours", 60 * 60 * 12),
    ("daily", 60 * 60 * 24),
]


VIEW_OPTIONS = []

METRIC_OPTIONS = [
    "Avg",
    "Sum",
    "Count",
    "p5",
    "p25",
    "p50",
    "p75",
    "p95",
    "Distinct",
]

class DatasetPresenter(object):
    def __init__(self, *args, **kwargs):
        self.table = kwargs['table']

    def get_views(self):
        ret = []
        for view in VIEW_OPTIONS:
            ret.append((view.get_display_name(), view.get_name()))

        return ret

    def get_metrics(self):
        return METRIC_OPTIONS

class QuerySpec(dotmap.DotMap):
    pass

# a virtual component has no assets,
# but its descendants might
@pudgy.Virtual
class ViewBase(pudgy.BackboneComponent):
    DISPLAY_NAME=""
    NAME="ViewBase"

    @classmethod
    def get_display_name(self):
        return self.DISPLAY_NAME or self.NAME

    @classmethod
    def get_name(self):
        return self.NAME

    def add_time_controls(self, controls):
        start_time = Selector(
            name="start",
            options=START_TIME_OPTIONS,
            selected=self.context.query.start)

        end_time = Selector(
            name="end",
            options=END_TIME_OPTIONS,
            selected=self.context.query.end)

        against_time = Selector(
            name="against",
            options=AGAINST_TIME_OPTIONS,
            selected=self.context.query.against)

        controls.append(ControlRow("start", "Start", start_time))
        controls.append(ControlRow("end", "End", end_time))
        controls.append(ControlRow("against", "Against", against_time))

    def add_view_selector(self, controls):
        view_selector = Selector(
            name="view",
            options=self.context.presenter.get_views(),
            selected=self.context.query.view)

        controls.append(ControlRow("view", "View", view_selector))

    def add_limit_selector(self, controls):
        limit_selector = TextInput(
            name="limit",
            value=self.context.query.limit)

        controls.append(ControlRow("limit", "Limit", limit_selector))

    def add_groupby_selector(self, controls):
        groups = make_dict(self.context.info["columns"]["strs"])
        groupby = MultiSelect(
            name="groupby[]",
            options=groups,
            selected=self.context.query.groupby)
        controls.append(ControlRow("groupby[]", "Group By", groupby))

    def add_metric_selector(self, controls):
        metric_selector = Selector(
            name="metric",
            options=self.context.presenter.get_metrics(),
            selected=self.context.query.table)

        controls.append(ControlRow("metric", "Metric", metric_selector))


    def add_field_selector(self, controls):
        fields = make_dict(self.context.info["columns"]["ints"])
        fields = Selector(
            name="field",
            options=fields,
            selected=self.context.query.field)
        controls.append(ControlRow("field", "Field", fields))

    def add_fields_selector(self, controls):
        fields = make_dict(self.context.info["columns"]["ints"])
        fields = MultiSelect(
            name="fields[]",
            options=fields,
            selected=self.context.query.fields)
        controls.append(ControlRow("fields[]", "Fields", fields))

    def add_go_button(self, controls):
        button = Button(name='go', className='go')
        controls.append(button)


    def get_controls(self):
        controls = []

        self.add_go_button(controls)
        self.add_view_selector(controls)
        self.add_time_controls(controls)

        self.add_groupby_selector(controls)
        self.add_limit_selector(controls)

        self.add_metric_selector(controls)
        self.add_fields_selector(controls)
        self.add_go_button(controls)

        return controls

class TableView(ViewBase, pudgy.JSComponent, pudgy.MustacheComponent):
    NAME="table"
    BASE="table"
    DISPLAY_NAME="Table View"

    def __prepare__(self):
        pass

class TimeView(ViewBase, pudgy.JSComponent):
    NAME="time"
    BASE="time"
    DISPLAY_NAME="Time View"


    def add_time_series_controls(self, controls):
        time_slice = Selector(
            name="time_bucket",
            options=TIME_SLICE_OPTIONS,
            selected=self.context.query.time_bucket)

        controls.append(ControlRow("time_bucket", "Time Slice", time_slice))

        normalize = Selector(
            name="time_normalize",
            options=[ "", "hour", "minute" ],
            selected=self.context.query.time_normalize)
        controls.append(ControlRow("time_normalize", "Normalize", normalize))



    def get_controls(self):
        controls = []

        self.add_go_button(controls)
        self.add_view_selector(controls)
        self.add_time_controls(controls)

        self.add_time_series_controls(controls)

        self.add_groupby_selector(controls)
        self.add_limit_selector(controls)

        self.add_metric_selector(controls)
        self.add_fields_selector(controls)
        self.add_go_button(controls)

        return controls


class DistView(ViewBase, pudgy.JSComponent):
    NAME="dist"
    BASE="dist"
    DISPLAY_NAME="Dist View"

    def get_controls(self):
        controls = []

        self.add_go_button(controls)
        self.add_view_selector(controls)
        self.add_time_controls(controls)

        self.add_groupby_selector(controls)
        self.add_limit_selector(controls)

        self.add_field_selector(controls)
        self.add_go_button(controls)

        return controls


class SamplesView(ViewBase, pudgy.JSComponent):
    NAME="samples"
    BASE="samples"
    DISPLAY_NAME="Samples View"

    def get_controls(self):
        controls = []

        self.add_go_button(controls)
        self.add_view_selector(controls)
        self.add_time_controls(controls)

        self.add_limit_selector(controls)

        self.add_go_button(controls)

        return controls


VIEW_OPTIONS = [ TableView, TimeView, DistView, SamplesView ]
def get_view_by_name(name):
    for cls in pudgy.util.inheritors(ViewBase):
        if cls.NAME.lower() == name.lower():
            return cls

class QuerySidebar(pudgy.BackboneComponent, pudgy.JinjaComponent, pudgy.SassComponent, pudgy.ServerBridge):
    def __prepare__(self):
        self.context.controls = self.context.view.get_controls()

@QuerySidebar.api
def run_query(cls, table=None, query=None, viewarea=None):
    # this is a name/value encoded array, unfortunately
    md = werkzeug.MultiDict()
    print "QUERY IS", query
    for q in query:
        if type(q) == dict:
            md.add(q['name'], q['value'].strip())
        elif type(q) == list or type(q) == tuple:
            md.add(q[0], q[1].strip())

    metric = md.get('metric')

    bs = backend.SybilBackend()
    res = bs.run_query(table, md)

    return {
        "query" : md.to_dict(flat=False),
        "results" : res }

@QuerySidebar.api
def update_controls(cls, table=None, view=None):
    p = DatasetPresenter(table=table)

    bs = backend.SybilBackend()
    ti = bs.get_table_info(table)

    query = QuerySpec(view=view)

    VwClass = get_view_by_name(view)

    v = VwClass(query=query)
    v.context.update(info=ti, presenter=p)

    qs = QuerySidebar(view=v, presenter=p)
    qs.marshal(table=table)
    cls.replace_html(qs.render())