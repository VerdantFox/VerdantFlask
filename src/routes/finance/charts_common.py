"""graphs_common: functions commonly used in graph production"""
from datetime import datetime
from math import pi
from typing import Optional, Union

import pandas as pd
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool, NumeralTickFormatter
from bokeh.palettes import viridis
from bokeh.plotting import figure
from bokeh.transform import cumsum, dodge

ChartHTML = tuple[str, str]


def produce_pie_chart(
    data_dict: dict[str, int], title: str, colors: Optional[list[str]] = None
) -> ChartHTML:
    """Produce a pie chart div, given data"""
    if not colors:
        colors = viridis(len(data_dict))
    data = (
        pd.Series(data_dict)
        .reset_index(name="value")
        .rename(columns={"index": "index"})
        .sort_values(by="value", ascending=False)
    )
    data["angle"] = data["value"] / data["value"].sum() * 2 * pi
    data["color"] = colors
    data["percentage"] = round(data["value"] / data["value"].sum() * 100)

    plot = figure(
        sizing_mode="scale_width",
        title=title,
        toolbar_location=None,
        tools="hover",
        tooltips="@index: $@value{,} (@percentage%)",
        x_range=(-0.5, 1.0),
    )

    plot.wedge(
        x=0,
        y=1,
        radius=0.4,
        start_angle=cumsum("angle", include_zero=True),
        end_angle=cumsum("angle"),
        line_color="white",
        fill_color="color",
        legend_field="index",
        source=data,
    )

    # Adjust plot settings
    adjust_plot_settings(plot, False)
    plot.axis.axis_label = None
    plot.axis.visible = False
    plot.grid.grid_line_color = None

    return components(plot)  # script, div


def produce_bar_chart(
    data_dict: dict[str, int], title: str, colors: Optional[list[str]] = None
) -> ChartHTML:
    """Produce a bar chart"""
    if not colors:
        colors = viridis(len(data_dict))
    x = list(data_dict.keys())
    dollars = list(data_dict.values())
    source = ColumnDataSource(data=dict(x=x, dollars=dollars, color=colors))
    plot = figure(
        sizing_mode="scale_width",
        title=title,
        toolbar_location=None,
        tools="hover",
        tooltips="@x: $@dollars{,}",
        x_range=x,
    )
    plot.vbar(
        x="x",
        top="dollars",
        width=0.9,
        source=source,
        line_color="white",
        color="color",
    )

    # Adjust plot settings
    adjust_plot_settings(plot)
    plot.yaxis[0].formatter = NumeralTickFormatter(format="$0,0")
    plot.xgrid.visible = False
    plot.ygrid.visible = False

    return components(plot)  # script, div


def produce_line_chart(
    x_val: list[Union[float, datetime]],
    y_vals: list[tuple[str, list[float]]],  # (legend_label, y_vals)
    title: str,
    x_axis_label: Optional[str] = None,
    y_axis_label: Optional[str] = None,
    colors: Optional[list[str]] = None,
) -> ChartHTML:
    """Produce a (multi-) line chart"""
    if not colors:
        colors = viridis(len(y_vals))
        assert isinstance(colors, str)

    hover = HoverTool(
        tooltips="@x{%m/%Y} $name: $@y{,}",
        formatters={"@x": "datetime"},
        mode="vline",
    )

    plot = figure(
        sizing_mode="scale_width",
        title=title,
        x_axis_label=x_axis_label,
        y_axis_label=y_axis_label,
        x_axis_type="datetime",
        tools=[hover],
        toolbar_location=None,
    )
    for i, (legend_label, y_val) in enumerate(y_vals):
        plot.line(
            x_val,
            y_val,
            legend_label=legend_label,
            line_color=colors[i],
            line_width=2,
            name=legend_label,
        )

    # Adjust plot settings
    adjust_plot_settings(plot)
    plot.yaxis[0].formatter = NumeralTickFormatter(format="$0,0")

    return components(plot)  # script, div


def produce_stacked_line_chart(
    x_val: list[Union[float]],
    y_vals: list[tuple[str, list[float]]],  # (legend_label, y_vals)
    title: str,
    x_axis_label: Optional[str] = None,
    y_axis_label: Optional[str] = None,
    colors: Optional[list[str]] = None,
) -> ChartHTML:
    """Produce a (multi-) line chart"""
    if not colors:
        colors = viridis(len(y_vals))
    hover = HoverTool(
        tooltips="@Date{%m/%Y} $name: $@$name{,}",
        formatters={"@Date": "datetime"},
        mode="vline",
    )
    plot = figure(
        sizing_mode="scale_width",
        title=title,
        x_axis_label=x_axis_label,
        y_axis_label=y_axis_label,
        x_axis_type="datetime",
        tools=[hover],
        toolbar_location=None,
        x_range=(x_val[0], x_val[-1]),
    )
    data = {"Date": x_val}

    for i, (legend_label, y_val) in enumerate(y_vals):
        data[legend_label] = y_val
    source = ColumnDataSource(data=data)
    y_labels = [y_val[0] for y_val in y_vals]
    plot.varea_stack(
        stackers=y_labels, x="Date", source=source, color=colors, legend_label=y_labels
    )
    plot.vline_stack(stackers=y_labels, x="Date", source=source, color=colors)

    # Adjust plot settings
    adjust_plot_settings(plot)
    plot.yaxis[0].formatter = NumeralTickFormatter(format="$0,0")
    plot.legend.background_fill_alpha = 0.9
    plot.legend.items.reverse()

    return components(plot)  # script, div


def produce_multi_bar_chart(
    data: dict[str, list[Union[str, int]]],
    x_label: str,
    legend_labels: list[str],
    title: str,
    colors: Optional[list[str]] = None,
):
    """Produce a multiple bar chart"""
    if not colors:
        colors = viridis(len(legend_labels))
        assert isinstance(colors, list)
    source = ColumnDataSource(data=data)

    plot = figure(
        sizing_mode="scale_width",
        title=title,
        toolbar_location=None,
        tools="hover",
        tooltips="@Years $name: $@$name{,}",
        x_range=data[x_label],
    )
    offsets = [-0.25, 0, 0.25]

    for i, legend_label in enumerate(legend_labels):
        plot.vbar(
            x=dodge("Years", offsets[i], range=plot.x_range),
            top=legend_label,
            width=0.2,
            source=source,
            color=colors[i],
            legend_label=legend_label,
            name=legend_label,
        )

    # Adjust plot settings
    adjust_plot_settings(plot)
    plot.yaxis[0].formatter = NumeralTickFormatter(format="$0,0")
    plot.xgrid.visible = False
    plot.ygrid.visible = False
    if len(data["Years"]) > 6:
        plot.xaxis.major_label_orientation = "vertical"

    return components(plot)  # script, div


def adjust_plot_settings(plot, legend=True):
    """Add common plot adjustments to plots"""
    plot.title.text_font_size = "1rem"
    plot.axis.major_label_text_font_size = "0.8rem"
    plot.xaxis.axis_label_text_font_size = "0.8rem"
    plot.yaxis.axis_label_text_font_size = "0.8rem"
    plot.border_fill_alpha = 0
    plot.background_fill_alpha = 0
    if legend:
        plot.legend.border_line_alpha = 0
        plot.legend.background_fill_alpha = 0.6


def combine_charts(*charts: tuple[str, str]) -> str:
    """Combine all chart data"""
    html = '<div class="row">'
    for i, (script, div) in enumerate(charts, start=1):
        if i % 2 == 1 and i != 1:
            html += '<div class="row">'
        html += f'<div class="col-lg-6"><div class="chart">{script}{div}</div></div>'
        if i % 2 == 0 or i == len(charts):
            html += "</div>"
    return html
