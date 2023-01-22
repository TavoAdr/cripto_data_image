from io         import BytesIO   as bt
from itertools  import compress  as cps
from time import sleep
from requests   import get       as gt
from PIL.Image  import open      as iop, new as inw
from json       import loads     as js
from matplotlib import pyplot    as plt

def fig2img(fig):
    
    """Convert a Matplotlib figure to a PIL Image and return it"""
    
    buf = bt()
    
    fig.savefig(buf, bbox_inches='tight')
    
    buf.seek(0)
    
    img = iop(buf)
    
    return img


def half( bigger, smaller, rest = 0 ):
    return ( bigger - smaller ) // 2 + rest


def coordinate( img_size : list[int, int], size : list[int, int], margin : list[int, int, int, int], align : list[int | str, int | str]) -> list[int, int] and list[int, int, int, int]:
    
    # Left
    if str(align[0]).lower() in ('1', 'l', 'left'):
        x = margin[0]
    
    # Center
    elif str(align[0]).lower() in ('2', 'c', 'center'):
        x = half(img_size[0], size[0], margin[1])
    
    # Right
    elif str(align[0]).lower() in ('3', 'r', 'right'):
        x = img_size[0] - margin[1] - size[0]

    # Top
    if str(align[1]).lower() in ('8', 't', 'top'):
        y = margin[2]
    
    # Middle
    elif str(align[1]).lower() in ('5', 'm', 'middle'):
        y = half(img_size[1], size[1], -margin[3])
    
    # Bottom
    elif str(align[1]).lower() in ('2', 'b', 'bottom'):
        y = img_size[1] - margin[3] - size[1]

    return [x, y], [x + size[0], size[0] + margin[1], y + size[1], size[1] + margin[3]]


def add_image( img1, size1, img2, size2, align, margin ):
    
    position, margin = coordinate(size1, size2, margin, align)
    img1.paste(img2, position, img2)

    return img1, margin


def create_table(col, row, val, title, clm_clr, colors):

    ax = plt.subplot(111, frame_on=False)
    ax.set_axis_off()
    
    table = ax.table( 
        cellText = val,  
        rowLabels = row,  
        colLabels = col,
        colWidths=[0.3 for x in col], 
        colLoc='left', 
        cellLoc ='left',  
        loc ='best',
        edges='horizontal',
    )

    for index, c in enumerate(clm_clr):
        for r in range( 1, len(row) + 1 ):
            table.get_celld()[(r,c)].get_text().set_color(colors[index][r-1])

    table.auto_set_font_size(False)
    table.set_fontsize(15)
    table.scale(1, 3)

    table.auto_set_column_width(col=list(range(len(col))))

    ax.set_title(title, fontweight ="bold", fontsize=20)


def cpc( coin, rows ):

    def prc():

        create_table(
            [
                '#',
                'Name',
                'Price',
                'Percent',
                'Last 7 Days'
            ],
            [
                ' '*6 for r in range(rows)
            ],
            [
                [
                    coin[r]['market_cap_rank'],
                    coin[r]['symbol'].upper(),
                    '${:,f}'.format(coin[r]['current_price']).rstrip('0') + ('00'
                        if isinstance(coin[r]['current_price'], int) else ''),
                    '{:.2f}%'.format(coin[r]['price_change_percentage_24h']),
                    ''
                ] for r in range(rows)
            ],
            'TOP ' + str(rows) + ' NON-STABLE CRYPTO',
            [3],
            [[ 'g' if coin[r]['price_change_percentage_24h'] > 0 else 'r' for r in range(rows)]]
        )

        background = inw(mode = "RGB", size = [1080,1920], color = ( 255, 255, 255 ))
        table = fig2img(plt)

        table = table.resize([int(background.size[0]), int(background.size[0] / table.size [0] * table.size[1])])

        add_image( background, background.size, table, table.size, [2, 5], [0,0,0,0] )

        margin = [0, 0, half(background.size[1], table.size[1]) + 180, 0]
        size = [ ( table.size[1] - 200 - 10 * rows ) // rows ] * 2

        for n in [coin[r] for r in range(rows)]:

            plt.clf()
            
            logo = iop(gt(n['image'], stream=True).raw).convert("RGBA")
            logo = logo.resize(size)

            top = margin[2] + 10
            background, margin = add_image( background, background.size, logo, logo.size, [1, 8], [20, 0, top, 0] )

            prices = n['sparkline_in_7d']['price']
            plt.plot( prices, color='r' if prices[0] > prices[len(prices)-1] else 'g', linewidth = 8 )
            plt.axis('off')
            plt.ylim( bottom = min(prices), top = max(prices) )
            chart = fig2img(plt)

            background, trash = add_image(
                img1    = background,
                size1   = background.size,
                img2    = chart.resize([ 300, size[0] - 10 ]),
                size2   = ( 300, size[0] - 10 ),
                align   = [ 3, 8 ],
                margin  = [ 0, 0, top, 0 ]
            )

        background.show()


    def pcp():

        create_table(
            [
                '#',
                'Name',
                '7D',
                '14D',
                '30D',
                '200D',
                '1Y'
            ],
            [
                ' '*6 for r in range(rows)
            ],
            [
                [
                    coin[r]['market_cap_rank'],
                    coin[r]['symbol'].upper(),

                    (
                        '{:.1f}%'.format(coin[r]['price_change_percentage_7d_in_currency'])
                            if -1 < coin[r]['price_change_percentage_7d_in_currency'] < 1
                            else '{:.0f}%'.format(coin[r]['price_change_percentage_7d_in_currency'])
                    ) if coin[r]['price_change_percentage_7d_in_currency'] else 'xXx',
                    
                    (
                        '{:.1f}%'.format(coin[r]['price_change_percentage_14d_in_currency'])
                            if -1 < coin[r]['price_change_percentage_14d_in_currency'] < 1
                            else '{:.0f}%'.format(coin[r]['price_change_percentage_14d_in_currency'])
                    ) if coin[r]['price_change_percentage_14d_in_currency'] else 'xXx',

                    (
                        '{:.1f}%'.format(coin[r]['price_change_percentage_30d_in_currency'])
                            if -1 < coin[r]['price_change_percentage_30d_in_currency'] < 1
                            else '{:.0f}%'.format(coin[r]['price_change_percentage_30d_in_currency'])
                    ) if coin[r]['price_change_percentage_30d_in_currency'] else 'xXx',
                    
                    (
                        '{:.1f}%'.format(coin[r]['price_change_percentage_200d_in_currency'])
                            if -1 < coin[r]['price_change_percentage_200d_in_currency'] < 1
                            else '{:.0f}%'.format(coin[r]['price_change_percentage_200d_in_currency'])
                    ) if coin[r]['price_change_percentage_200d_in_currency'] else 'xXx',
                    
                    (
                        '{:.1f}%'.format(coin[r]['price_change_percentage_1y_in_currency'])
                            if -1 < coin[r]['price_change_percentage_1y_in_currency'] < 1
                            else '{:.0f}%'.format(coin[r]['price_change_percentage_1y_in_currency'])
                    ) if coin[r]['price_change_percentage_1y_in_currency'] else 'xXx'
                
                ] for r in range(rows)
            ],
            'PRICE CHANGE PERCENT',
            [2, 3, 4, 5, 6],
            [
                [
                    'g' if coin[r]['price_change_percentage_7d_in_currency'] and coin[r]['price_change_percentage_7d_in_currency'] > 0
                    else 'r' for r in range(rows)
                ],
                [
                    'g' if coin[r]['price_change_percentage_14d_in_currency'] and coin[r]['price_change_percentage_14d_in_currency'] > 0
                    else 'r' for r in range(rows)
                ],
                [
                    'g' if coin[r]['price_change_percentage_30d_in_currency'] and coin[r]['price_change_percentage_30d_in_currency'] > 0
                    else 'r' for r in range(rows)
                ],
                [
                    'g' if coin[r]['price_change_percentage_200d_in_currency'] and coin[r]['price_change_percentage_200d_in_currency'] > 0
                    else 'r' for r in range(rows)
                ],
                [
                    'g' if coin[r]['price_change_percentage_1y_in_currency'] and coin[r]['price_change_percentage_1y_in_currency'] > 0
                    else 'r' for r in range(rows)
                ],
            ]
        )
        
        background = inw(mode = "RGB", size = [1080,1920], color = ( 255, 255, 255 ))
        table = fig2img(plt)

        table = table.resize([int(background.size[0]), int(background.size[0] / table.size [0] * table.size[1])])

        add_image( background, background.size, table, table.size, [2, 5], [0,0,0,0] )

        margin = [0, 0, half(background.size[1], table.size[1]) + 180, 0]
        size = [ ( table.size[1] - 200 - 10 * rows ) // rows ] * 2

        for n in [coin[r] for r in range(rows)]:

            plt.clf()
            
            logo = iop(gt(n['image'], stream=True).raw).convert("RGBA")
            logo = logo.resize(size)

            background, margin = add_image( background, background.size, logo, logo.size, [1, 8], [20, 0, margin[2] + 10, 0] )

        background.show()


    def ath():

        ath_per = [ -coin[r]['ath_change_percentage'] for r in range(rows) ]
        
        def remap(x, in_min, in_max, out_min, out_max):
            return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
        
        pos = [ str(hex(int(remap(ath_per[r], min(ath_per), max(ath_per), 0, 255)))).replace('0x', '') for r in range(rows) ]

        create_table(
            [
                '#',
                'Name',
                'ATH',
                'Drop',
                'Date'
            ],
            [
                ' '*6 for r in range(rows)
            ],
            [
                [
                    coin[r]['market_cap_rank'],
                    coin[r]['symbol'].upper(),
                    
                    '${:,f}'.format(coin[r]['ath']).rstrip('0') + ('00'
                        if isinstance(coin[r]['ath'], int) else ''),

                    (
                        '{:.1f}%'.format(coin[r]['ath_change_percentageentage'])
                        if -1 < coin[r]['ath_change_percentage'] < 1
                        else '{:.0f}%'.format(coin[r]['ath_change_percentage'])
                    ) if coin[r]['ath_change_percentage'] else 0,
                    
                    coin[r]['ath_date'][2:10],

                ] for r in range(rows)
            ],
            'ALL-TIME HIGH',
            [3],
            [
                [ 
                    '#' + ( pos[r] if len(pos[r]) > 1 else '0' + pos[r] ) + '0000' for r in range(rows)
                ]
            ]
        )
        
        background = inw(mode = "RGB", size = [1080,1920], color = ( 255, 255, 255 ))
        table = fig2img(plt)

        table = table.resize([int(background.size[0]), int(background.size[0] / table.size [0] * table.size[1])])

        add_image( background, background.size, table, table.size, [2, 5], [0,0,0,0] )

        margin = [0, 0, half(background.size[1], table.size[1]) + 180, 0]
        size = [ ( table.size[1] - 200 - 10 * rows ) // rows ] * 2

        for n in [coin[r] for r in range(rows)]:

            plt.clf()
            
            logo = iop(gt(n['image'], stream=True).raw).convert("RGBA")
            logo = logo.resize(size)

            background, margin = add_image( background, background.size, logo, logo.size, [1, 8], [20, 0, margin[2] + 10, 0] )

        background.show()


    prc()
    pcp()
    ath()


def main():

    criptos = js(gt('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&sparkline=true&price_change_percentage=24h%2C7d%2C14d%2C30d%2C200d%2C1y').content)
    stable = [ s['id'] for s in js(gt('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category=stablecoins&order=market_cap_desc&per_page=250&page=1&sparkline=falsehttps://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category=stablecoins&order=market_cap_desc&per_page=250&page=1&sparkline=false').content) ]
    cpc(list(cps(criptos,[i not in stable for i in [ c['id'] for c in criptos ]])), 15)

    trend = js(gt('https://api.coingecko.com/api/v3/search/trending').content)
    coins = [t['item']['id'] for t in trend['coins']]
    search = js(gt(
        'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids='
        + str(coins).replace(', ', '%2C').replace('[', '').replace('\'', '').replace(']', '') +
        '&order=market_cap_desc&per_page=250&page=1&sparkline=true&price_change_percentage=24h%2C7d%2C14d%2C30d%2C200d%2C1y'
    ).content)
    cpc(search, len(search))

    exit()

    # top 10
    coin_list([1080,1920], (255,255,255), font, coin, 'current_price', 'price_change_percentage_24h', 1).show()

    # fall to ath
    coin_list([1080,1920], (255,255,255), font, coin, 'ath', 'ath_change_percentage', 0).show()

if __name__ == '__main__':
    main()