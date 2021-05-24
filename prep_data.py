import pandas as pd
import plotly.express as px
import numpy as np
from plotly import graph_objects as go
from itertools import chain

FILENAME = "ankieta okręgowa statsy prep.xls"
COLS_DICT = {}
UNFILTERED_COLS_DICT = {}

def read_data(filename=FILENAME):
    return pd.read_excel(filename)

def split_col(df, colname=None):
    df[colname].fillna('',inplace=True)
    unique_vals = {s.strip() for s in chain.from_iterable(df[colname].str.split(',').to_list())}
    if 'itd)' in unique_vals:
        unique_vals.remove('itd)')
    if '' in unique_vals:
        unique_vals.remove('')
    for uv in unique_vals:
        df[uv] = df[colname].apply(lambda x: 1 if x is not np.nan and uv in x else 0)
    return list(unique_vals)


def custom_columns_preproc(okr_data):
    okr_data = okr_data.rename(columns={
        'Podaj swoją płeć': 'płeć',
        'Podaj swój wiek (w latach)': 'wiek',
        'Jakie masz wykształcenie?': 'wykształcenie',
        'Podaj swój zawód (opcjonalne)': 'zawód',
        'Jak oceniasz swój stopień aktywności w partii?': 'stopień aktywności',
        'Jak często zaglądasz na okręgowego Slacka?': 'częstotliwość slackowania',
        'Jak oceniasz działalność okręgu z ostatniego pół roku?': 'ocena okręgu',
        'Jak oceniasz działalność zarządu z ostatniego pół roku?': 'ocena zarządu',
        'Jak oceniasz działalność partii ogólnie z ostatniego pół roku?': 'ocena partii',
        'Ile średnio godzin w tygodniu poświęcasz na działalność partyjną?': 'obecna dostępność czasowa',
        'Ile średnio godzin w tygodniu jesteś teoretycznie w stanie poświęcać na działalność partyjną?': 'potencjalna dostępność czasowa',
        'Jak długo jesteś w Razem jako członek lub sympatyk? (podaj liczbę miesięcy; rok=12 miesięcy)': 'staż w partii (miesiące)',
        'Co skłoniło Cię do dołączenia do partii?': 'przyczyny dołączenia',
        'Jakie kwestie związane z działalnością lewicy są dla Ciebie najistotniejsze? (zaznacz max 3 odpowiedzi)': 'istotne_lewica',
        'Jakie kwestie związane z działalnością okręgu są dla Ciebie najważniejsze? (zaznacz max 3 odpowiedzi)': 'istotne_okręg',
        'Przyczyny, dla których nie działasz aktywnie w okręgu: (wybierz max 3, jeśli działasz aktywnie, pomiń ten krok)': 'przyczyny braku aktywności',
        'Przyczyny, dla których NIE zdecydował*ś się kandydować do Zarządu: (wybierz max 3, jeśli kandydujesz/jesteś w obecnym zarządzie/nie chcesz odpowiadać, pomiń ten krok)': 'przyczyny nie kandydowania'

    })
    okr_data = pd.concat([okr_data,
                          pd.get_dummies(okr_data['stopień aktywności'])], axis=1)
    okr_data['stosunek potencjalnej dostępności do obecnej'] = okr_data['potencjalna dostępność czasowa'] / okr_data[
        'obecna dostępność czasowa']
    okr_data['potencjalny wzrost dostępności czasowej'] = okr_data['potencjalna dostępność czasowa'] - okr_data[
        'obecna dostępność czasowa']

    active_cols = ['brak aktywności', 'tylko płacę składki', 'niska aktywność',
                   'średnia aktywność', 'wysoka aktywność']
    UNFILTERED_COLS_DICT['aktywność'] = active_cols
    COLS_DICT['aktywność'] = active_cols

    join_reasons_cols = split_col(okr_data, colname='przyczyny dołączenia')
    UNFILTERED_COLS_DICT['przyczyny dołączenia'] = join_reasons_cols
    join_reasons_cols.remove(
        'Oprócz poparcia partii chce by partia rozszerzyła program o wsparcie osób pracujących seksualnie i praw pracowniczych dla nich')
    join_reasons_cols.remove('poczucie możliwości zmiany na lepsze')
    COLS_DICT['przyczyny dołączenia'] = join_reasons_cols

    left_imp_cols = split_col(okr_data, colname='istotne_lewica')
    okr_data = okr_data.rename(columns={'''usługi publiczne (ochrona zdrowia''': "usługi publiczne"})
    left_imp_cols = ["usługi publiczne" if el.strip() == "usługi publiczne (ochrona zdrowia" else el.strip()
                     for el in left_imp_cols]
    UNFILTERED_COLS_DICT['istotne tematy lewicowe'] = left_imp_cols
    left_imp_cols.remove('ochrona zdrowia - rozwiązania systemowe')
    left_imp_cols.remove('Sprawy związane z ekonomia')
    left_imp_cols.remove('transport')
    left_imp_cols.remove('gospodarka')
    COLS_DICT['istotne tematy lewicowe'] = left_imp_cols

    okr_imp_cols = split_col(okr_data, colname='istotne_okręg')
    okr_data = okr_data.rename(columns={
        '''działania związane z usługami publicznymi (ochrona zdrowia''': "działania związane z usługami publicznymi"})
    okr_imp_cols = [
        "działania związane z usługami publicznymi" if el.strip() == "działania związane z usługami publicznymi (ochrona zdrowia" else el.strip()
        for el in okr_imp_cols]
    UNFILTERED_COLS_DICT['istotne obszary działania okręgu'] = okr_imp_cols
    okr_imp_cols.remove('transport')
    COLS_DICT['istotne obszary działania okręgu'] = okr_imp_cols

    imp_action_cols = ['najważniejsza akcja: brak',
                       'najważniejsza akcja: panel klimatyczny',
                       'najważniejsza akcja: strajk kobiet',
                       'najważniejsza akcja: płodoboardy',
                       'najważniejsza akcja: ławki/skwer praw kobiet',
                       'najważniejsza akcja: Wesoła',
                       'najważniejsza akcja: kontrola szpitali',
                       'najważniejsza akcja: wsparcie (operatorów) dźwigów',
                       'najważniejsza akcja: szkoła zsm4']
    UNFILTERED_COLS_DICT['najważniejsze akcje'] = imp_action_cols
    imp_action_cols.remove('najważniejsza akcja: panel klimatyczny')
    imp_action_cols.remove('najważniejsza akcja: szkoła zsm4')
    COLS_DICT['najważniejsze akcje'] = imp_action_cols

    act_inc_cols = ['wzrost aktywności: możliwość łatwego zapoznania się z bieżącymi zadaniami',
                    'wzrost aktywności: więcej uwagi dla istotnych dla mnie tematów',
                    'wzrost aktywności: lepsze zagospodarowanie nowych członków i włączenie ich w akcje',
                    'wzrost aktywności: większa aktywność/słowność pozostałych członków/członkiń',
                    'wzrost aktywności: podniesienie kompetencji',
                    'wzrost aktywności: więcej czasu',
                    'wzrost aktywności: więcej akcji/więcej działań w moim zakresie kompetencji',
                    'wzrost aktywności: poprawa organizacji okręgu',
                    'wzrost aktywności: jeśniej zdefiniowane zadania',
                    'wzrost aktywności: koniec pandemii/więcej interakcji na żywo',
                    'wzrost aktywności: sprawy osobiste',
                    'wzrost aktywności: lepsze samopoczucie',
                    'wzrost aktywności: klarowna strategia i cele',
                    'wzrost aktywności: integracja']
    UNFILTERED_COLS_DICT['wzrost aktywności'] = act_inc_cols
    act_inc_cols.remove('wzrost aktywności: większa aktywność/słowność pozostałych członków/członkiń')
    act_inc_cols.remove('wzrost aktywności: więcej uwagi dla istotnych dla mnie tematów')
    COLS_DICT['wzrost aktywności'] = act_inc_cols

    longterm_cols = ['długofalowe cele: walka o prawa pracownicze/kwestie socjalne',
                     'długofalowe cele: nawiązanie współpracy/sojuszy z innymi organizacjami',
                     'długofalowe cele: organizacja finansów okręgu',
                     'długofalowe cele: działalność proekologiczna',
                     'długofalowe cele: poprawa wizerunku lewicy',
                     'długofalowe cele: poprawa współpracy z biurem poselskim',
                     'długofalowe cele: wypracowanie procedur wdrażania osób członkowskich',
                     'długofalowe cele: aktywizm lokalny',
                     'długofalowe cele: zwiększenie liczby osób członkowskich',
                     'długofalowe cele: propagowanie lewicowych wartości',
                     'długofalowe cele: umacnianie partii w województwie',
                     'długofalowe cele: przygotowanie do wyborów (samorządowych i/lub parlamentarnych)/promocja kandydatów',
                     'długofalowe cele: widoczność w mediach/rozpoznawalność',
                     'długofalowe cele: aktywizacja członków']
    UNFILTERED_COLS_DICT['długofalowe cele okręgu'] = longterm_cols
    longterm_cols.remove('długofalowe cele: organizacja finansów okręgu')
    longterm_cols.remove('długofalowe cele: wypracowanie procedur wdrażania osób członkowskich')
    COLS_DICT['długofalowe cele okręgu'] = longterm_cols

    short_term_cols = ['działania na najbliższe miesiące: współpraca z innymi organizacjami',
                       'działania na najbliższe miesiące: Turnicki Park Narodowy i inne działania prośrodowiskowe',
                       'działania na najbliższe miesiące: poprawa sytuacji osób niepełnosprawnych i w kryzysie bezdomności w kontekście szczepień/inne akcje związane z covidem',
                       'działania na najbliższe miesiące: rozwój struktur, budowa partii w powiecie',
                       'działania na najbliższe miesiące: pomoc branży gastronomicznej i współpraca ze związkami zawodowymi',
                       'działania na najbliższe miesiące: realizacja programu ze spotkania walnego',
                       'działania na najbliższe miesiące: przygotowanie do wyborów samorządowych',
                       'działania na najbliższe miesiące: integracja/aktywizacja osób członkowskich/szkolenia',
                       'działania na najbliższe miesiące: nowe akcje/aktywizm',
                       'działania na najbliższe miesiące: poprawa przepływu informacji',
                       'działania na najbliższe miesiące: rozwój social mediów/obecność w sieci',
                       'działania na najbliższe miesiące: zwiększenie rozpoznawalności partii',
                       'działania na najbliższe miesiące: poprawa organizacji',
                       'działania na najbliższe miesiące: zdefiniowanie celów']
    UNFILTERED_COLS_DICT['krótkofalowe cele okręgu'] = short_term_cols
    short_term_cols.remove(
        'działania na najbliższe miesiące: poprawa sytuacji osób niepełnosprawnych i w kryzysie bezdomności w kontekście szczepień/inne akcje związane z covidem')
    short_term_cols.remove('działania na najbliższe miesiące: poprawa przepływu informacji')
    short_term_cols.remove('działania na najbliższe miesiące: współpraca z innymi organizacjami')
    COLS_DICT['krótkofalowe cele okręgu'] = short_term_cols

    adm_func_cols = ['funkcje zarządu: brak odpowiedzi',
                     'funkcje zarządu: przygotowanie do wyborów',
                     'funkcje zarządu: reakcje na wydarzenia bieżące',
                     'funkcje zarządu: moderacja/rozwiązywanie konfliktów',
                     'funkcje zarządu: wspieranie członków w akcjach',
                     'funkcje zarządu: organizacja pracy i koordynacja działań',
                     'funkcje zarządu: finanse',
                     'funkcje zarządu: administracja',
                     'funkcje zarządu: kontakt z mediami/reprezentacyjna',
                     'funkcje zarządu: współpraca ze strukturami centralnymi',
                     'funkcje zarządu: opracowanie agendy, strategii i postulatów',
                     'funkcje zarządu: selekcja i promowanie kandydatów',
                     'funkcje zarządu: edukacyjna',
                     'funkcje zarządu: decyzyjność',
                     'funkcje zarządu: wprowadzanie nowych członków',
                     'funkcje zarządu: propagowanie informacji/sprawozdawczość',
                     'funkcje zarządu: współpraca z innymi organizacjami/samorządem',
                     'funkcje zarządu: współpraca z posłanką',
                     'funkcje zarządu: moblilizacja/budowa struktur okręgowych']
    UNFILTERED_COLS_DICT['funkcje zarządu'] = adm_func_cols
    adm_func_cols.remove('funkcje zarządu: finanse')
    adm_func_cols.remove('funkcje zarządu: selekcja i promowanie kandydatów')
    COLS_DICT['funkcje zarządu'] = adm_func_cols

    noactive_reasons_cols = split_col(okr_data, colname='przyczyny braku aktywności')
    okr_data['brak czasu na działania partyjne'] = okr_data[
        ['brak czasu na działania partyjne',
         'tymczasowa konieczność pracowania po godzinach',
         'O ile byłem aktywny jakiś czas temu to z przyczyn osobistych',
         'że już niedługo będę miał trochę więcej czasu i wrócę do działania.',
         'musiałem ograniczyć działania partyje (i wiele innych)ml. Liczę jednak',
         'Rozpoczęcie studiów magisterskich z budownictwa']].any(axis=1)

    okr_data['nie znam bierzących zadań'] = okr_data[
        [
            'nie jestem informowany/a o działaniach',
            'troche nie wiem',
            'co moglbym robic',
            'Dopiero dołączyłam i dopiero mogę działać od kilku dni'
        ]
    ].any(axis=1)

    okr_data['zły stan psychiczny z powodu ogólnie'] = okr_data[
        [
            'zły stan psychiczny z powodu ogólnie',
            'aktywne uczestniczenie w życiu politycznym źle wpływa na stan mojego zdrowia prychicznego'
        ]
    ].any(axis=1)
    for el in [
        'tymczasowa konieczność pracowania po godzinach',
        'O ile byłem aktywny jakiś czas temu to z przyczyn osobistych',
        'że już niedługo będę miał trochę więcej czasu i wrócę do działania.',
        'musiałem ograniczyć działania partyje (i wiele innych)ml. Liczę jednak',
        'Rozpoczęcie studiów magisterskich z budownictwa',
        'nie jestem informowany/a o działaniach',
        'troche nie wiem',
        'co moglbym robic',
        'Dopiero dołączyłam i dopiero mogę działać od kilku dni',
        'aktywne uczestniczenie w życiu politycznym źle wpływa na stan mojego zdrowia prychicznego'
    ]:
        noactive_reasons_cols.remove(el)
    noactive_reasons_cols.append('nie znam bierzących zadań')
    UNFILTERED_COLS_DICT['przyczyny braku aktywności'] = noactive_reasons_cols
    COLS_DICT['przyczyny braku aktywności'] = noactive_reasons_cols

    #nocandidate_reasons_cols = split_col(okr_data, colname='przyczyny nie kandydowania')
    return okr_data, UNFILTERED_COLS_DICT, COLS_DICT


def prep_data():
    okr_data = read_data()
    return custom_columns_preproc(okr_data)