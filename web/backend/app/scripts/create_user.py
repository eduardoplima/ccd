"""Cria ou atualiza um usuário em Usuarios.

Uso (requer rede TCE para chegar no BdDIP):

    uv run --package ccd-web-backend python -m app.scripts.create_user \
        --login eduardo --email eplima.cc@gmail.com --nome "Eduardo Lima" --papel admin

Pede a senha via getpass, valida o limite de 72 bytes do bcrypt e faz UPSERT por login.
`Usuarios` não tem nome completo separado; `--nome` é aceito por compatibilidade
mas não é persistido (o login é o NomeUsuario).
"""

from __future__ import annotations

import getpass
import sys

import click
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import FRAPUsuario
from app.auth.security import BCRYPT_MAX_BYTES, hash_password
from app.db import session_scope


@click.command()
@click.option("--login", required=True, help="Login do usuário (chave única de autenticação).")
@click.option("--email", default=None, help="E-mail do usuário (opcional).")
@click.option("--nome", required=True, help="Nome completo.")
@click.option(
    "--papel",
    type=click.Choice(["user", "admin"], case_sensitive=False),
    default="user",
    show_default=True,
)
@click.option(
    "--senha",
    default=None,
    help="Senha em claro. Se omitida, será solicitada via prompt seguro.",
)
@click.option(
    "--forcar-troca/--sem-forcar-troca",
    "forcar_troca",
    default=True,
    show_default=True,
    help="Obriga o usuário a trocar a senha no primeiro acesso (senha provisória).",
)
def main(
    login: str, email: str | None, nome: str, papel: str, senha: str | None, forcar_troca: bool
) -> None:
    senha_via_flag = senha is not None
    if not senha_via_flag:
        senha = getpass.getpass("Senha: ")
        if senha != getpass.getpass("Confirme a senha: "):
            click.echo("As senhas não conferem.", err=True)
            sys.exit(2)
    assert senha is not None
    if len(senha.encode("utf-8")) > BCRYPT_MAX_BYTES:
        click.echo(f"Senha excede {BCRYPT_MAX_BYTES} bytes (limite do bcrypt).", err=True)
        sys.exit(2)

    senha_hash = hash_password(senha)
    login_norm = login.strip().lower()
    email_norm = email.strip().lower() if email else None

    for session in session_scope():
        _upsert(session, login_norm, email_norm, nome.strip(), papel.lower(), senha_hash, forcar_troca)


def _upsert(
    session: Session,
    login: str,
    email: str | None,
    nome: str,
    papel: str,
    senha_hash: str,
    forcar_troca: bool,
) -> None:
    _ = nome  # não persistido em Usuarios
    existente = session.scalar(select(FRAPUsuario).where(FRAPUsuario.Login == login))
    if existente is None:
        session.add(
            FRAPUsuario(
                Login=login,
                Email=email,
                SenhaHash=senha_hash,
                Papel=papel,
                Ativo=True,
                DeveTrocarSenha=forcar_troca,
            )
        )
        session.commit()
        click.echo(f"Usuário criado: {login} (papel={papel}, forcar_troca={forcar_troca})")
        return

    if email is not None:
        existente.Email = email
    existente.Papel = papel
    existente.SenhaHash = senha_hash
    existente.Ativo = True
    existente.DeveTrocarSenha = forcar_troca
    session.commit()
    click.echo(f"Usuário atualizado: {login} (papel={papel}, forcar_troca={forcar_troca})")


if __name__ == "__main__":
    main()
