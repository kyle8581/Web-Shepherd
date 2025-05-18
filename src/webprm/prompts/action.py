ACTION_SPACE_PROMPT = """Note: This action set allows you to interact with your environment. Most of them are python function executing playwright code. The primary way of referring to elements in the page is through bid which are specified in your observations.

15 different types of actions are available.

noop(wait_ms: float = 1000)
    Examples:
        noop()

        noop(500)

scroll(delta_x: float, delta_y: float)
    Examples:
        scroll(0, 200)

        scroll(-50.2, -100.5)

keyboard_press(key: str)
    Examples:
        keyboard_press('Backspace')

        keyboard_press('ControlOrMeta+a')

        keyboard_press('Meta+Shift+t')

click(bid: str, button: Literal['left', 'middle', 'right'] = 'left', modifiers: list[typing.Literal['Alt', 'Control', 'ControlOrMeta', 'Meta', 'Shift']] = [])
    Examples:
        click('a51')

        click('b22', button='right')

        click('48', button='middle', modifiers=['Shift'])

fill(bid: str, value: str)
    Examples:
        fill('237', 'example value')

        fill('45', 'multi-line\nexample')

        fill('a12', 'example with "quotes"')

hover(bid: str)
    Examples:
        hover('b8')

tab_focus(index: int)
    Examples:
        tab_focus(2)

new_tab()
    Examples:
        new_tab()

go_back()
    Examples:
        go_back()

go_forward()
    Examples:
        go_forward()

goto(url: str)
    Examples:
        goto('http://www.example.com')

tab_close()
    Examples:
        tab_close()

select_option(bid: str, options: str | list[str])
    Examples:
        select_option('a48', 'blue')

        select_option('c48', ['red', 'green', 'blue'])

send_msg_to_user(text: str)
    Examples:
        send_msg_to_user('Based on the results of my search, the city was built in 1751.')

report_infeasible(reason: str)
    Examples:
        report_infeasible('I cannot follow these instructions because there is no email field in this form.')

Only a single action can be provided at once. Example:
fill('a12', 'example with "quotes"')

Note:
* Some tasks may be game like and may require to interact with the mouse position in x, y coordinates.
* Some text field might have auto completion. To see it, you have to type a few characters and wait until next step.
* If you have to cut and paste, don't forget to select the text first.
* Coordinate inside an SVG are relative to it's top left corner.
* Make sure to use bid to identify elements when using commands.
* Interacting with combobox, dropdowns and auto-complete fields can be tricky, sometimes you need to use select_option, while other times you need to use fill or click and wait for the reaction of the page.
"""