from covid import Covid

covid21 = Covid(source='worldometers')


def get_country_name():
    countries_list = covid21.list_countries()
    for item in countries_list:
        print(item)
    country_name = input('Enter the country name: ')
    if country_name != "exit":
        while not (country_name in countries_list):
            country_name = input("Enter the country name: ")
        return country_name
    else:
        exit(1)


def print_statistics_by_country(country):
    print('Covid statistics in the country: ', country['country'])
    print('Confirmed: ', country['confirmed'])
    print('Deaths: ', country['deaths'])
    print('Recovered: ', country['recovered'], )
    print('Active: ', country['active'])


def main():
    name = get_country_name()
    country_info_by_name = covid21.get_status_by_country_name(name)
    print_statistics_by_country(country_info_by_name)


if __name__ == '__main__':
    main()
