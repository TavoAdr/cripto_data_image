from itertools import compress
import string
from time import sleep
import requests, json
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt

def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    import io
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img

 
def half( size1, size2 ):
    return ( size1 - size2 ) // 2


def coordinate( img_size : list[int, int], size : list[int, int], margin : list[int, int, int, int], align : list[int | str, int | str]) -> list[int, int] and list[int, int, int, int]:
    
    # Left
    if str(align[0]).lower() in ('1', 'l', 'left'):
        x = margin[0]
    
    # Center
    elif str(align[0]).lower() in ('2', 'c', 'center'):
        x = half(img_size[0], size[0])  + margin[1]
    
    # Right
    elif str(align[0]).lower() in ('3', 'r', 'right'):
        x = img_size[0] - margin[1] - size[0]

    # Top
    if str(align[1]).lower() in ('8', 't', 'top'):
        y = margin[2]
    
    # Middle
    elif str(align[1]).lower() in ('5', 'm', 'middle'):
        y = half(img_size[1], size[1]) - margin[3]
    
    # Bottom
    elif str(align[1]).lower() in ('2', 'b', 'bottom'):
        y = img_size[1] - margin[3] - size[1]

    return [x, y], [x + size[0], size[0] + margin[1], y + size[1], size[1] + margin[3]]


def add_text(draw : ImageDraw, text : str, font : ImageFont, color : list[int, int, int], image_size : list[int, int], align : list[int, int], margin : list[int, int, int, int]):

    position, margin = coordinate(image_size, draw.textsize(text,font=font), margin, align)
    
    draw.text(
        xy              = position,
        text            = text,
        font            = font,
        fill            = color
    )

    return margin


def add_image( img1, size1, img2, size2, align, margin ):
    
    position, margin = coordinate(size1, size2, margin, align)
    img1.paste(img2, position, img2)

    return img1, margin


def coin_list( image_size, bg_color, font, item, price, percent, price_chart ):

    img     = Image.new(mode = "RGB", size = image_size, color=bg_color)
    draw    = ImageDraw.Draw(img)

    size = draw.textsize(string.ascii_letters, font=font )[1] * 2

    for index, i in enumerate(item):

        name = str(i['market_cap_rank']) + ' - ' + i['name'] + ' : ' + i['symbol'].upper()
        logo = Image.open(requests.get(i['image'], stream=True).raw).convert("RGBA")
        top = index * ( size + 60 )

        img, margin = add_image(
            img1    = img,
            size1   = img.size,
            img2    = logo.resize([size, size]),
            size2   = [size, size],
            align   = [1,8],
            margin  = [ 20, 0, top + 20, 0 ]
        )

        margin = add_text(
            draw        = draw,
            text        = name,
            font        = font,
            color       = (0, 0, 0),
            image_size  = image_size,
            align       = [1,8],
            margin      = (
                margin[0] + 10,
                0, top + 15, 0
            )
        )

        margin = add_text(
            draw        = draw,
            text        = "${:,.2f}".format(i[price]),
            font        = font,
            color       = (0, 0, 0),
            image_size  = image_size,
            align       = [1,8],
            margin      = (
                30 + size,
                0,
                margin[2],
                0
            )
        )

        change_percent = i[percent]

        margin = add_text(
            draw        = draw,
            text        = ' +{:.2f}%'.format(change_percent) if change_percent > 0 else ' {:.2f}%'.format(change_percent),
            font        = font,
            color       = 'green' if change_percent > 0 else 'red',
            image_size  = image_size,
            align       = [1,8],
            margin      = (
                margin[0] + 5,
                0,
                top + size / 2 + 10,
                0
            )
        )

        if price_chart:
            prices = i['sparkline_in_7d']['price']
            plt.plot(prices, color='red' if prices[0] > prices[len(prices)-1] else 'green', linewidth=5)
            plt.axis('off')
            plt.ylim(bottom=min(prices), top=max(prices))
            chart = fig2img(plt.gcf())

            img, margin = add_image(
                img1    = img,
                size1   = img.size,
                img2    = chart.resize([400,100]),
                size2   = (400,100),
                align   = [3,8],
                margin  = [
                    0,
                    margin[1],
                    top,
                    0
                ]
            )

        if index > 8:
            break
        
    return img

        # add_text = str(c['market_cap_rank']) + ' ' +str(c[price])+str(c['market_cap'])+str(c['ath'])+str(c['ath_change_percentage'])

    #     draw.text(
    #         xy      = (x,y),
    #         text    = text,
    #         font    = font,
    #         fill    = (0,0,0),
    #     )

    #     y += 150


criptos = json.loads(requests.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&sparkline=true&price_change_percentage=24h%2C7d%2C30d%2C1y').content)

stable = [ s['id'] for s in json.loads(requests.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category=stablecoins&order=market_cap_desc&per_page=250&page=1&sparkline=falsehttps://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category=stablecoins&order=market_cap_desc&per_page=250&page=1&sparkline=false').content) ]

not_stable = list(compress(criptos,[i not in stable for i in [ c['id'] for c in criptos ]]))

font = ImageFont.truetype("Ubuntu-B.ttf", 40)
# top 10
coin_list([1080,1920], (255,255,255), font, not_stable, 'current_price', 'price_change_percentage_24h', 1).show()

# fall to ath
coin_list([1080,1920], (255,255,255), font, not_stable, 'ath', 'ath_change_percentage', 0).show()
