from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from core.game import Game
from core.player import Player
from core.bank import Bank
from starlette.responses import HTMLResponse
from core.utils import reset_game

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="."), name="static")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# game/player settings
bank = Bank(saldo=0)
new_game = Game(bank=bank, slots=[], bet_price=0, logs=[])
player = Player(coins=100_000, ganhos=0)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/jogo")
async def home(request: Request):
    new_game.girar_roleta()

    return templates.TemplateResponse(
        request=request,
        name="jogo.html",
        context={"slots": new_game.slots, "player": player, "bank": bank},
    )


@app.get("/reset-saldo")
async def reset_saldo(request: Request):
    reset_game(player, new_game)

    return {"saldo": player.coins}


@app.post("/girar")
async def girar_roleta(request: Request, bet_price: float = None):
    new_game.bet_price = bet_price
    response = new_game.girar_roleta(player)

    if response["status"] == "error":
        raise HTTPException(status_code=403, detail="Sem saldo")
    
    # Atualizar o saldo do jogador com base no ganho ou perda
    player.coins += response.get("apenas_ganho", 0) - new_game.bet_price

    return templates.TemplateResponse(
        "slot_desenho.html",
        {
            "request": request,
            "slots": new_game.slots,
            "results": response.get("results", []),
            "apenas_ganho": response.get("apenas_ganho", 0),
            "player": player,  # O saldo atualizado do jogador
            "logs": new_game.logs,
            "bank": bank,
        },
    )

@app.get("/sacar")
async def sacar(request: Request):
    # Zera o saldo do jogador
    player.coins = 0
    
    # Retorna a imagem de saque
    return templates.TemplateResponse("saque.html", {"request": request})

@app.get("/primos")
async def primos(request: Request):
    return templates.TemplateResponse("primos.html", {"request": request})