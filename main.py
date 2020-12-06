import phraser

# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    ashen = phraser.pagePhrase('ashen077')
    print(ashen.page_count())
    charts = ashen.track_lists('https://www.last.fm/user/ashen077/library?page=3')
    print(charts)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
