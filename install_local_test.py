#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
import datetime
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


HOME = Path.home()

PROJECT = HOME / "dayz/modding/ZellnoPrisonBear"
BUILD_MOD = PROJECT / "build/@ZellnoPrisonBear"

SERVER = HOME / "dayz/server"
SERVER_MOD = SERVER / "@ZellnoPrisonBear"
SERVER_KEY = SERVER / "keys/Zellno.bikey"

CLIENT = HOME / ".local/share/Steam/steamapps/common/DayZ"
CLIENT_MOD = CLIENT / "@ZellnoPrisonBear"

START_SH = SERVER / "start.sh"
CONNECT_SH = HOME / "dayz_connect.sh"
FIX_LINKS = HOME / "dayz/tools/fix_dayz_client_mod_links.py"

PUBLIC_KEY = (
    HOME / "dayz/modding/keys/Zellno/Zellno.bikey"
)

MOD_NAME = "@ZellnoPrisonBear"

BACKUP_ROOT = HOME / "dayz/backups"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_file(path: Path) -> None:
    if not path.is_file():
        raise RuntimeError(f"Arquivo obrigatório ausente: {path}")


def require_directory(path: Path) -> None:
    if not path.is_dir():
        raise RuntimeError(f"Diretório obrigatório ausente: {path}")


def server_is_running() -> bool:
    for process_name in ("DayZServer", "enfMain"):
        result = subprocess.run(
            ["pgrep", "-x", process_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )

        if result.returncode == 0:
            return True

    return False


def updated_mod_line(path: Path) -> tuple[str, bool]:
    text = path.read_text(encoding="utf-8")

    pattern = re.compile(
        r'(?m)^(?P<prefix>-mod=")'
        r'(?P<mods>[^"]*)'
        r'(?P<suffix>".*)$'
    )

    matches = list(pattern.finditer(text))

    if len(matches) != 1:
        raise RuntimeError(
            f"Esperava exatamente uma linha -mod em: {path}"
        )

    match = matches[0]
    mods = [
        item
        for item in match.group("mods").split(";")
        if item
    ]

    if MOD_NAME in mods:
        return text, False

    mods.append(MOD_NAME)

    replacement = (
        match.group("prefix")
        + ";".join(mods)
        + match.group("suffix")
    )

    updated = (
        text[:match.start()]
        + replacement
        + text[match.end():]
    )

    return updated, True


def updated_fix_links(path: Path) -> tuple[str, bool]:
    text = path.read_text(encoding="utf-8")

    pattern = re.compile(
        r"(?m)^MODS = (?P<value>\[[^\n]*\])$"
    )

    matches = list(pattern.finditer(text))

    if len(matches) != 1:
        raise RuntimeError(
            f"Esperava exatamente uma declaração MODS em: {path}"
        )

    match = matches[0]

    try:
        mods = ast.literal_eval(match.group("value"))
    except (SyntaxError, ValueError) as exc:
        raise RuntimeError(
            f"Não foi possível interpretar MODS em: {path}"
        ) from exc

    if not isinstance(mods, list):
        raise RuntimeError("MODS não é uma lista.")

    if MOD_NAME in mods:
        return text, False

    mods.append(MOD_NAME)

    replacement = f"MODS = {mods!r}"

    updated = (
        text[:match.start()]
        + replacement
        + text[match.end():]
    )

    return updated, True


def directories_equal(left: Path, right: Path) -> bool:
    if not left.is_dir() or not right.is_dir():
        return False

    left_files = {
        path.relative_to(left)
        for path in left.rglob("*")
        if path.is_file()
    }
    right_files = {
        path.relative_to(right)
        for path in right.rglob("*")
        if path.is_file()
    }

    if left_files != right_files:
        return False

    return all(
        sha256(left / relative) == sha256(right / relative)
        for relative in left_files
    )


def describe_client() -> str:
    if CLIENT_MOD.is_symlink():
        return f"link -> {CLIENT_MOD.resolve(strict=False)}"
    if CLIENT_MOD.exists():
        return "caminho real existente"
    return "ausente"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Instala Zellno Prison Bear de forma reversível."
        )
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica a integração; sem esta opção, apenas simula.",
    )
    args = parser.parse_args()

    require_directory(BUILD_MOD)
    require_file(
        BUILD_MOD / "addons/ZellnoPrisonBear.pbo"
    )
    require_file(
        BUILD_MOD
        / "addons/ZellnoPrisonBear.pbo.Zellno.bisign"
    )
    require_file(BUILD_MOD / "keys/Zellno.bikey")
    require_file(PUBLIC_KEY)
    require_file(SERVER_KEY)
    require_file(START_SH)
    require_file(CONNECT_SH)
    require_file(FIX_LINKS)
    require_directory(CLIENT)

    build_key = BUILD_MOD / "keys/Zellno.bikey"

    expected_key_hash = sha256(PUBLIC_KEY)

    for candidate in (build_key, SERVER_KEY):
        if sha256(candidate) != expected_key_hash:
            raise RuntimeError(
                f"Chave Zellno divergente: {candidate}"
            )

    new_start, change_start = updated_mod_line(START_SH)
    new_connect, change_connect = updated_mod_line(CONNECT_SH)
    new_fix, change_fix = updated_fix_links(FIX_LINKS)

    server_correct = directories_equal(
        BUILD_MOD,
        SERVER_MOD,
    )

    client_correct = (
        CLIENT_MOD.is_symlink()
        and CLIENT_MOD.resolve(strict=False)
        == SERVER_MOD.resolve(strict=False)
    )

    changes = {
        "server_mod": not server_correct,
        "client_link": not client_correct,
        "start_sh": change_start,
        "connect_sh": change_connect,
        "fix_links": change_fix,
    }

    print("=" * 76)
    print(" Zellno Prison Bear — instalação local")
    print("=" * 76)
    print()
    print(f"Modo: {'APLICAÇÃO' if args.apply else 'SIMULAÇÃO'}")
    print()
    print(f"Build:    {BUILD_MOD}")
    print(f"Servidor: {SERVER_MOD}")
    print(f"Cliente:  {CLIENT_MOD}")
    print()
    print(f"Servidor atual: "
          f"{'homologado' if server_correct else 'ausente ou divergente'}")
    print(f"Cliente atual:  {describe_client()}")
    print()
    print("Alterações necessárias:")
    for name, needed in changes.items():
        print(f"  {name:<14} {'SIM' if needed else 'NÃO'}")

    if not any(changes.values()):
        print()
        print("Estado já correto. Nenhuma alteração necessária.")
        return 0

    if not args.apply:
        print()
        print("SIMULAÇÃO concluída. Nenhum arquivo foi alterado.")
        print("Use --apply somente após conferir este relatório.")
        return 0

    if server_is_running():
        raise RuntimeError(
            "O DayZServer está rodando. Encerre-o antes de aplicar."
        )

    timestamp = datetime.datetime.now().strftime(
        "%Y%m%d-%H%M%S"
    )
    backup = (
        BACKUP_ROOT
        / f"install-zellno-prison-bear-{timestamp}"
    )
    backup.mkdir(parents=True, exist_ok=False)

    shutil.copy2(START_SH, backup / "start.sh")
    shutil.copy2(CONNECT_SH, backup / "dayz_connect.sh")
    shutil.copy2(
        FIX_LINKS,
        backup / "fix_dayz_client_mod_links.py",
    )

    server_existed = (
        SERVER_MOD.exists() or SERVER_MOD.is_symlink()
    )
    client_existed = (
        CLIENT_MOD.exists() or CLIENT_MOD.is_symlink()
    )

    if server_existed:
        if SERVER_MOD.is_symlink():
            (backup / "server_mod_symlink.txt").write_text(
                os.readlink(SERVER_MOD),
                encoding="utf-8",
            )
        elif SERVER_MOD.is_dir():
            shutil.copytree(
                SERVER_MOD,
                backup / "@ZellnoPrisonBear.server",
            )
        else:
            shutil.copy2(
                SERVER_MOD,
                backup / "@ZellnoPrisonBear.server",
            )

    if client_existed:
        if CLIENT_MOD.is_symlink():
            (backup / "client_mod_symlink.txt").write_text(
                os.readlink(CLIENT_MOD),
                encoding="utf-8",
            )
        elif CLIENT_MOD.is_dir():
            shutil.copytree(
                CLIENT_MOD,
                backup / "@ZellnoPrisonBear.client",
            )
        else:
            shutil.copy2(
                CLIENT_MOD,
                backup / "@ZellnoPrisonBear.client",
            )

    stage = Path(
        tempfile.mkdtemp(
            prefix=".ZellnoPrisonBear-stage-",
            dir=SERVER,
        )
    )

    try:
        staged_mod = stage / "@ZellnoPrisonBear"
        shutil.copytree(BUILD_MOD, staged_mod)

        if not directories_equal(BUILD_MOD, staged_mod):
            raise RuntimeError(
                "A cópia temporária diverge do build."
            )

        if SERVER_MOD.is_symlink():
            SERVER_MOD.unlink()
        elif SERVER_MOD.is_dir():
            shutil.rmtree(SERVER_MOD)
        elif SERVER_MOD.exists():
            SERVER_MOD.unlink()

        shutil.move(str(staged_mod), str(SERVER_MOD))

        if CLIENT_MOD.is_symlink():
            CLIENT_MOD.unlink()
        elif CLIENT_MOD.is_dir():
            shutil.rmtree(CLIENT_MOD)
        elif CLIENT_MOD.exists():
            CLIENT_MOD.unlink()

        CLIENT_MOD.symlink_to(
            SERVER_MOD,
            target_is_directory=True,
        )

        START_SH.write_text(new_start, encoding="utf-8")
        CONNECT_SH.write_text(new_connect, encoding="utf-8")
        FIX_LINKS.write_text(new_fix, encoding="utf-8")

        if not directories_equal(BUILD_MOD, SERVER_MOD):
            raise RuntimeError(
                "Mod instalado diverge do build homologado."
            )

        if not CLIENT_MOD.is_symlink():
            raise RuntimeError(
                "Link do cliente não foi criado."
            )

        if CLIENT_MOD.resolve() != SERVER_MOD.resolve():
            raise RuntimeError(
                "Link do cliente aponta para destino incorreto."
            )

        final_start, pending_start = updated_mod_line(START_SH)
        final_connect, pending_connect = updated_mod_line(
            CONNECT_SH
        )
        final_fix, pending_fix = updated_fix_links(FIX_LINKS)

        if pending_start or pending_connect or pending_fix:
            raise RuntimeError(
                "A integração não ficou idempotente."
            )

    except Exception:
        shutil.copy2(backup / "start.sh", START_SH)
        shutil.copy2(
            backup / "dayz_connect.sh",
            CONNECT_SH,
        )
        shutil.copy2(
            backup / "fix_dayz_client_mod_links.py",
            FIX_LINKS,
        )

        if CLIENT_MOD.is_symlink():
            CLIENT_MOD.unlink()
        elif CLIENT_MOD.is_dir():
            shutil.rmtree(CLIENT_MOD)
        elif CLIENT_MOD.exists():
            CLIENT_MOD.unlink()

        if SERVER_MOD.is_symlink():
            SERVER_MOD.unlink()
        elif SERVER_MOD.is_dir():
            shutil.rmtree(SERVER_MOD)
        elif SERVER_MOD.exists():
            SERVER_MOD.unlink()

        server_backup = backup / "@ZellnoPrisonBear.server"
        server_link = backup / "server_mod_symlink.txt"

        if server_backup.is_dir():
            shutil.copytree(server_backup, SERVER_MOD)
        elif server_backup.is_file():
            shutil.copy2(server_backup, SERVER_MOD)
        elif server_link.is_file():
            SERVER_MOD.symlink_to(
                server_link.read_text(encoding="utf-8")
            )

        client_backup = backup / "@ZellnoPrisonBear.client"
        client_link = backup / "client_mod_symlink.txt"

        if client_backup.is_dir():
            shutil.copytree(client_backup, CLIENT_MOD)
        elif client_backup.is_file():
            shutil.copy2(client_backup, CLIENT_MOD)
        elif client_link.is_file():
            CLIENT_MOD.symlink_to(
                client_link.read_text(encoding="utf-8")
            )

        raise

    finally:
        if stage.exists():
            shutil.rmtree(stage)

    print()
    print("INSTALAÇÃO concluída.")
    print(f"Backup: {backup}")
    print("O servidor não foi iniciado.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        raise SystemExit(1)
