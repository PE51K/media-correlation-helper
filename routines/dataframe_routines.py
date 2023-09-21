import pandas as pd


def pretty_dataframe(dataframe):
    dataframe.columns = dataframe.iloc[0]
    dataframe.drop(dataframe.index[0], inplace=True)
    dataframe.drop('campaign_id', axis=1, inplace=True)
    dataframe.drop('platform', axis=1, inplace=True)

    dataframe = type_dataframe(dataframe)
    dataframe = clear_zeros(dataframe)
    dataframe = add_click_rate_to_dataframe(dataframe)
    dataframe = add_drug_name_to_dataframe(dataframe)
    dataframe = add_medic_group_to_dataframe(dataframe)
    dataframe = add_adv_format_to_dataframe(dataframe)
    dataframe = add_campaign_numbers_to_dataframe(dataframe)

    dataframe = add_rolling_mean_to_dataframe(dataframe, window=3)
    dataframe = add_rolling_mean_to_dataframe(dataframe, window=5)
    dataframe = add_rolling_mean_to_dataframe(dataframe, window=7)

    dataframe = add_trend_flag_to_dataframe(dataframe)
    dataframe = add_moving_average_change_to_dataframe(dataframe)

    dataframe = add_day_of_campaign(dataframe)

    return dataframe


def clear_zeros(dataframe):
    dataframe = dataframe[(dataframe['clicks'] > 0) | (dataframe['impressions'] > 100)]
    dataframe = dataframe.drop(
        dataframe.loc[dataframe['impressions'] < dataframe['clicks']].index)  # 1 клик при 0 показов
    return dataframe


# noinspection SpellCheckingInspection
def type_dataframe(dataframe):
    dataframe['campaign_name'] = dataframe['campaign_name'].str.lower()
    dataframe.loc[:, 'date'] = pd.to_datetime(dataframe['date'], format='%m/%d/%Y')
    dataframe['impressions'] = pd.to_numeric(dataframe['impressions'], errors='coerce').fillna(0)
    dataframe['clicks'] = pd.to_numeric(dataframe['clicks'], errors='coerce').fillna(0)

    return dataframe


# noinspection SpellCheckingInspection
def add_click_rate_to_dataframe(dataframe):
    dataframe['click_rate'] = dataframe['clicks'] / dataframe['impressions']

    return dataframe


# noinspection SpellCheckingInspection
def add_drug_name_to_dataframe(dataframe):
    dataframe.loc[(dataframe.campaign_name.str.contains('dexonal')) | (
        dataframe.campaign_name.str.contains('дексонал')), 'drug_name'] = 'dexonal'
    dataframe.loc[(dataframe.campaign_name.str.contains('диклофенак')) | (
        dataframe.campaign_name.str.contains('diclofenac')), 'drug_name'] = 'diclofenac_akos'
    dataframe.loc[(dataframe.campaign_name.str.contains('maxilac')) | (
        dataframe.campaign_name.str.contains('максилак')), 'drug_name'] = 'maxilac'
    dataframe.loc[(dataframe.campaign_name.str.contains('кагоцел')) | (
        dataframe.campaign_name.str.contains('kagocel')), 'drug_name'] = 'kagocel'
    dataframe.loc[(dataframe.campaign_name.str.contains('венарус')) | (
        dataframe.campaign_name.str.contains('venarus')), 'drug_name'] = 'venarus'
    dataframe.loc[(dataframe.campaign_name.str.contains('необутин')) | (
        dataframe.campaign_name.str.contains('neobutin')), 'drug_name'] = 'neobutin'
    dataframe.loc[(dataframe.campaign_name.str.contains('эльмуцин')) | (
        dataframe.campaign_name.str.contains('elmucin')), 'drug_name'] = 'elmucin'
    dataframe.loc[(dataframe.campaign_name.str.contains('парацитолгин')) | (
        dataframe.campaign_name.str.contains('paracitolgin')), 'drug_name'] = 'paracitolgin'
    dataframe.loc[(dataframe.campaign_name.str.contains('акнауцер')) | (
        dataframe.campaign_name.str.contains('aknaucer')), 'drug_name'] = 'aknaucer'
    dataframe.loc[dataframe['drug_name'].isna(), 'drug_name'] = 'none'

    return dataframe


# noinspection SpellCheckingInspection
def add_medic_group_to_dataframe(dataframe):
    dataframe.loc[(dataframe.campaign_name.str.contains('фармацевт')) | (
        dataframe.campaign_name.str.contains('pharma')), 'medic_group'] = 'pharmacy'
    dataframe.loc[(dataframe.campaign_name.str.contains('терапевт')) | (
        dataframe.campaign_name.str.contains('terapist')) | (
                      dataframe.campaign_name.str.contains(
                          'therapist')), 'medic_group'] = 'therapist'
    dataframe.loc[(dataframe.campaign_name.str.contains('pediatrician')) | (
        dataframe.campaign_name.str.contains('педиатр')), 'medic_group'] = 'pediatricias'
    dataframe.loc[(dataframe.campaign_name.str.contains('surgeon')) | (
        dataframe.campaign_name.str.contains('хирург')), 'medic_group'] = 'surgeon'
    dataframe.loc[(dataframe.campaign_name.str.contains('neurologist')) | (
        dataframe.campaign_name.str.contains('невролог')), 'medic_group'] = 'neurologist'
    dataframe.loc[(dataframe.campaign_name.str.contains('gastro')) | (
        dataframe.campaign_name.str.contains('гастро')), 'medic_group'] = 'gastro'
    dataframe.medic_group = dataframe.medic_group.fillna('none')

    return dataframe


# noinspection SpellCheckingInspection
def add_adv_format_to_dataframe(dataframe):
    dataframe.loc[(dataframe.campaign_name.str.contains('carousel')) | (
        dataframe.campaign_name.str.contains('carusel')), 'adv_format'] = 'carousel'
    dataframe.loc[
        (dataframe.campaign_name.str.contains('баннеры')) | (
            dataframe.campaign_name.str.contains('banner')), 'adv_format'] = 'banner'
    dataframe.loc[(dataframe.campaign_name.str.contains('video')) | (
        dataframe.campaign_name.str.contains('видео')), 'adv_format'] = 'video'
    dataframe.loc[
        (dataframe.campaign_name.str.contains('multiformat')), 'adv_format'] = 'multiformat'
    dataframe.loc[
        ~((dataframe.campaign_name.str.contains('carousel')) | (
            dataframe.campaign_name.str.contains('carusel')) |
          (dataframe.campaign_name.str.contains('баннеры')) | (
              dataframe.campaign_name.str.contains('banner')) |
          (dataframe.campaign_name.str.contains('video')) | (
              dataframe.campaign_name.str.contains('видео')) |
          (dataframe.campaign_name.str.contains('multiformat'))), 'adv_format'] = 'others'

    return dataframe


def add_campaign_numbers_to_dataframe(dataframe, window=14):
    dataframe.sort_values(['campaign_name', 'adv_format', 'date'], inplace=True)

    current_campaign = 0
    previous_date = None
    previous_campaign_info = None

    campaign_numbers = []

    for index, row in dataframe.iterrows():
        if previous_date is None or (row['date'] - previous_date).days > window:
            current_campaign += 1
        elif row['campaign_name'] != previous_campaign_info[0] or \
                row['adv_format'] != previous_campaign_info[1]:
            current_campaign = 1

        campaign_numbers.append(current_campaign)
        previous_date = row['date']
        previous_campaign_info = (row['campaign_name'], row['adv_format'])

    dataframe['campaign_number'] = campaign_numbers

    return dataframe


def add_rolling_mean_to_dataframe(dataframe, window=3):
    dataframe[f'rolled_{window}'] = dataframe.groupby(['campaign_name', 'campaign_number']).click_rate.ewm(
        span=window, min_periods=window, adjust=False).mean().values

    return dataframe


def add_trend_flag_to_dataframe(dataframe):
    trend_flags = []

    for current_row in dataframe[['rolled_7', 'rolled_5', 'rolled_3']].values:
        if not current_row[0]:
            trend_flags.append('Not enough data')
        if current_row[0] > current_row[1] > current_row[2]:
            trend_flags.append('Decrease')
        elif current_row[2] > current_row[1] > current_row[0]:
            trend_flags.append('Increase')
        else:
            trend_flags.append('Plateau')

    dataframe['trend'] = trend_flags
    return dataframe


def add_moving_average_change_to_dataframe(dataframe):
    dataframe['percentage_change'] = dataframe.groupby(['campaign_name', 'campaign_number'])['rolled_5'].pct_change() * 100
    dataframe['moving_average_change'] = dataframe.groupby(['campaign_name', 'campaign_number'])['percentage_change'].rolling(
        window=3).mean().reset_index(level=[0, 1], drop=True)

    dataframe.moving_average_change.fillna(0, inplace=True)
    dataframe = dataframe.drop('percentage_change', axis=1)

    return dataframe


def add_day_of_campaign(dataframe):
    dataframe.sort_values(['drug_name', 'medic_group', 'adv_format', 'campaign_number', 'date'], inplace=True)

    dataframe['day'] = dataframe.groupby(['drug_name', 'medic_group', 'adv_format', 'campaign_number']).cumcount() + 1

    dataframe.reset_index(drop=True, inplace=True)

    return dataframe
