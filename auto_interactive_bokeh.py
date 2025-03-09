def create_interactive_plot(data_df,
                            x_column,
                            y_column,
                            plot_title="Interactive Plot",
                            plot_width=800,
                            plot_height=400,
                            parameters=None,
                            callback_functions=None,
                            output_filename="interactive_plot.html"):
    """
    Creates an interactive Bokeh plot with automated JavaScript callbacks.

    Parameters:
    -----------
    data_df : pandas DataFrame
        The DataFrame containing the data to plot
    x_column : str
        The column name to use for x-axis
    y_column : str
        The column name to use for y-axis
    plot_title : str
        The title of the plot
    plot_width : int
        Width of the plot in pixels
    plot_height : int
        Height of the plot in pixels
    parameters : dict
        A dictionary of parameters to create sliders/inputs for.
        Format: {
            'param_name': {
                'type': 'slider' or 'text' or 'select',
                'title': 'Display Title',
                'value': initial_value,
                'start': min_value,  # For sliders
                'end': max_value,    # For sliders
                'step': step_size,   # For sliders
                'options': [list, of, options]  # For select
            }
        }
    callback_functions : dict
        A dictionary of JavaScript callback functions for each parameter.
        Format: {
            'param_name': 'JavaScript function as string that updates the data',
        }
    output_filename : str
        Filename for the HTML output

    Returns:
    --------
    layout : bokeh layout
        The complete Bokeh layout that can be shown with show(layout)
    """
    from bokeh.plotting import figure
    from bokeh.io import output_file
    from bokeh.layouts import column, row
    from bokeh.models import ColumnDataSource, CustomJS
    from bokeh.models.widgets import Slider, TextInput, Select

    # Configure output
    output_file(output_filename)

    # Create a copy of the original data for reference
    data_df = data_df.copy()
    for col in data_df.columns:
        data_df[f"{col}_original"] = data_df[col].copy()

    # Create the ColumnDataSource
    source = ColumnDataSource(data_df)

    # Create the figure
    plot = figure(
        title=plot_title,
        width=plot_width,
        height=plot_height,
        tools="pan,wheel_zoom,box_zoom,reset,save,crosshair"
    )

    # Add the main line or scatter plot
    plot.line(x_column, y_column, source=source, line_width=2)

    # Create widgets and callbacks
    widgets = []
    if parameters:
        # Title widget is special - always create it
        title_input = TextInput(title="Plot Title", value=plot_title)
        title_callback = CustomJS(args=dict(plot=plot), code="""
            plot.title.text = cb_obj.value;
        """)
        title_input.js_on_change('value', title_callback)
        widgets.append(title_input)

        # Create all the parameter widgets
        for param_name, param_config in parameters.items():
            if param_config['type'] == 'slider':
                widget = Slider(
                    title=param_config['title'],
                    value=param_config['value'],
                    start=param_config['start'],
                    end=param_config['end'],
                    step=param_config.get('step', 1)
                )
            elif param_config['type'] == 'text':
                widget = TextInput(
                    title=param_config['title'],
                    value=str(param_config['value'])
                )
            elif param_config['type'] == 'select':
                widget = Select(
                    title=param_config['title'],
                    value=str(param_config['value']),
                    options=param_config['options']
                )
            else:
                continue

            # Get the specific callback for this parameter or use a default
            if callback_functions and param_name in callback_functions:
                callback_code = callback_functions[param_name]
            else:
                # Default callback simply logs the change
                callback_code = f"""
                    console.log("{param_name} changed to: " + cb_obj.value);
                """

            # Create the callback
            callback = CustomJS(args=dict(source=source, param=widget), code=callback_code)
            widget.js_on_change('value', callback)
            widgets.append(widget)

    # Create and return the layout
    layout = column(plot, *widgets)
    return layout


# Example usage with automatically generated callbacks
def demo_auto_callbacks():
    import pandas as pd
    import numpy as np

    # Create sample data
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    data = pd.DataFrame({'x': x, 'y': y})

    # Define parameters
    parameters = {
        'amplitude': {
            'type': 'slider',
            'title': 'Amplitude',
            'value': 1.0,
            'start': 0.1,
            'end': 3.0,
            'step': 0.1
        },
        'frequency': {
            'type': 'slider',
            'title': 'Frequency',
            'value': 1.0,
            'start': 0.1,
            'end': 3.0,
            'step': 0.1
        },
        'offset': {
            'type': 'slider',
            'title': 'Y Offset',
            'value': 0.0,
            'start': -2.0,
            'end': 2.0,
            'step': 0.1
        },
        'line_type': {
            'type': 'select',
            'title': 'Line Type',
            'value': 'Sine',
            'options': ['Sine', 'Cosine', 'Linear']
        }
    }

    # Create automated callbacks
    callbacks = {
        'amplitude': '''
            const data = source.data;
            const amplitude = cb_obj.value;
            const frequency = param.document._all_models['frequency'].value;
            const offset = param.document._all_models['offset'].value;
            const line_type = param.document._all_models['line_type'].value;

            const x = data['x_original'];
            const y = data['y'];

            for (let i = 0; i < x.length; i++) {
                if (line_type === 'Sine') {
                    y[i] = amplitude * Math.sin(frequency * x[i]) + offset;
                } else if (line_type === 'Cosine') {
                    y[i] = amplitude * Math.cos(frequency * x[i]) + offset;
                } else {
                    // Linear
                    y[i] = amplitude * x[i] + offset;
                }
            }

            source.change.emit();
        ''',
        'frequency': '''
            const data = source.data;
            const frequency = cb_obj.value;
            const amplitude = param.document._all_models['amplitude'].value;
            const offset = param.document._all_models['offset'].value;
            const line_type = param.document._all_models['line_type'].value;

            const x = data['x_original'];
            const y = data['y'];

            for (let i = 0; i < x.length; i++) {
                if (line_type === 'Sine') {
                    y[i] = amplitude * Math.sin(frequency * x[i]) + offset;
                } else if (line_type === 'Cosine') {
                    y[i] = amplitude * Math.cos(frequency * x[i]) + offset;
                } else {
                    // Linear
                    y[i] = amplitude * x[i] + offset;
                }
            }

            source.change.emit();
        ''',
        'offset': '''
            const data = source.data;
            const offset = cb_obj.value;
            const amplitude = param.document._all_models['amplitude'].value;
            const frequency = param.document._all_models['frequency'].value;
            const line_type = param.document._all_models['line_type'].value;

            const x = data['x_original'];
            const y = data['y'];

            for (let i = 0; i < x.length; i++) {
                if (line_type === 'Sine') {
                    y[i] = amplitude * Math.sin(frequency * x[i]) + offset;
                } else if (line_type === 'Cosine') {
                    y[i] = amplitude * Math.cos(frequency * x[i]) + offset;
                } else {
                    // Linear
                    y[i] = amplitude * x[i] + offset;
                }
            }

            source.change.emit();
        ''',
        'line_type': '''
            const data = source.data;
            const line_type = cb_obj.value;
            const amplitude = param.document._all_models['amplitude'].value;
            const frequency = param.document._all_models['frequency'].value;
            const offset = param.document._all_models['offset'].value;

            const x = data['x_original'];
            const y = data['y'];

            for (let i = 0; i < x.length; i++) {
                if (line_type === 'Sine') {
                    y[i] = amplitude * Math.sin(frequency * x[i]) + offset;
                } else if (line_type === 'Cosine') {
                    y[i] = amplitude * Math.cos(frequency * x[i]) + offset;
                } else {
                    // Linear
                    y[i] = amplitude * x[i] + offset;
                }
            }

            source.change.emit();
        '''
    }

    # Create the plot
    layout = create_interactive_plot(
        data_df=data,
        x_column='x',
        y_column='y',
        plot_title='Interactive Function Plot',
        parameters=parameters,
        callback_functions=callbacks,
        output_filename='auto_callbacks_demo.html'
    )

    return layout


# Example usage with callback generator function
def create_callback_generator(transformation_code):
    """
    Creates a callback generator function that produces JavaScript callbacks
    based on a template and transformation code.

    Parameters:
    -----------
    transformation_code : str
        JavaScript code that transforms the data

    Returns:
    --------
    generator : function
        A function that generates callbacks for each parameter
    """

    def generator(param_name, param_list):
        """
        Generates a specific callback for a parameter.

        Parameters:
        -----------
        param_name : str
            The name of the parameter to create a callback for
        param_list : list
            List of all parameter names that will be used in the callback

        Returns:
        --------
        callback : str
            The JavaScript callback code
        """
        # Create the parameter retrieval section
        param_retrieval = []
        for p in param_list:
            if p == param_name:
                param_retrieval.append(f"const {p} = cb_obj.value;")
            else:
                param_retrieval.append(f"const {p} = param.document._all_models['{p}'].value;")

        param_code = '\n    '.join(param_retrieval)

        # Create the full callback
        callback = f"""
            const data = source.data;

            // Get all parameters
            {param_code}

            // Get data arrays
            const x = data['x_original'];
            const y = data['y'];

            // Apply transformation
            {transformation_code}

            // Notify of changes
            source.change.emit();
        """

        return callback

    return generator


# Example of using the callback generator
def demo_callback_generator():
    import pandas as pd
    import numpy as np

    # Create sample data
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    data = pd.DataFrame({'x': x, 'y': y})

    # Define parameters
    parameters = {
        'amplitude': {
            'type': 'slider',
            'title': 'Amplitude',
            'value': 1.0,
            'start': 0.1,
            'end': 3.0,
            'step': 0.1
        },
        'frequency': {
            'type': 'slider',
            'title': 'Frequency',
            'value': 1.0,
            'start': 0.1,
            'end': 3.0,
            'step': 0.1
        },
        'offset': {
            'type': 'slider',
            'title': 'Y Offset',
            'value': 0.0,
            'start': -2.0,
            'end': 2.0,
            'step': 0.1
        }
    }

    # Create a transformation template
    transformation_code = """
        for (let i = 0; i < x.length; i++) {
            y[i] = amplitude * Math.sin(frequency * x[i]) + offset;
        }
    """

    # Create the callback generator
    generator = create_callback_generator(transformation_code)

    # Generate callbacks for each parameter
    param_list = list(parameters.keys())
    callbacks = {
        param: generator(param, param_list) for param in param_list
    }

    # Create the plot
    layout = create_interactive_plot(
        data_df=data,
        x_column='x',
        y_column='y',
        plot_title='Generated Callbacks Demo',
        parameters=parameters,
        callback_functions=callbacks,
        output_filename='generated_callbacks_demo.html'
    )

    return layout