       {"name": "pasta", "label": "Pasta", "field": "pasta", "align": "left", "sortable": True},
    {"name": "nome", "label": "Nome", "field": "nome", "align": "left", "sortable": True},
    {"name": "conteudo", "label": "Conteúdo", "field": "conteudo", "align": "left"},
    {"name": "link", "label": "Pasta Digitalizada", "field": "link", "align": "left"},
]


@ui.page("/")
def main_page() -> None:
    search_input: ui.input
    item_table: ui.table
    dialog: ui.dialog
    total_label: ui.label
    fields: dict[str, Any] = {}
    current_id: int | None = None

    def refresh_table() -> None:
        item_table.rows = list_items(search_input.value or "")
        item_table.update()
        total_label.set_text(f"{len(item_table.rows)} registro(s) exibido(s)")

    def close_dialog() -> None:
        dialog.close()

    def save_form() -> None:
        data = {key: str(field.value or "").strip() for key, field in fields.items()}
        if not data["nome"] and not data["conteudo"]:
            ui.notify("Informe o nome ou o conteúdo do convênio.", type="warning")
            return
        save_item(data, current_id)
        close_dialog()
        refresh_table()
        ui.notify("Registro salvo com sucesso.", type="positive")

    def confirm_delete() -> None:
        if current_id is None:
            return
        with ui.dialog() as confirmation:
            with ui.card().classes("w-96"):
                ui.label("Excluir registro?").classes("text-h6")
                ui.label("Esta ação não poderá ser desfeita.").classes("text-gray-600")
                with ui.row().classes("w-full justify-end gap-2 mt-4"):
                    ui.button("Cancelar", on_click=confirmation.close).props("flat")
                    def do_delete() -> None:
                        delete_item(current_id)
                        confirmation.close()
                        close_dialog()
                        refresh_table()
                        ui.notify("Registro excluído.", type="positive")
                    ui.button("Excluir", color="negative", on_click=do_delete)
        confirmation.open()

    def open_form(item: dict[str, Any] | None = None) -> None:
        nonlocal current_id
        current_id = item["id"] if item else None
        dialog.clear()
        with dialog, ui.card().classes("w-full max-w-4xl"):
            ui.label("Editar convênio" if item else "Adicionar convênio").classes("text-h5")
            ui.label("Informe os dados do convênio, parceria ou instrumento administrativo.").classes("text-gray-600 mb-3")
            with ui.column().classes("w-full gap-2"):
                fields["pasta"] = ui.input("Pasta", value=str(item.get("pasta", "") if item else "")).props("outlined dense")
                fields["nome"] = ui.textarea("Nome", value=str(item.get("nome", "") if item else "")).props("outlined autogrow")
                fields["conteudo"] = ui.textarea("Conteúdo", value=str(item.get("conteudo", "") if item else "")).props("outlined autogrow")
                fields["link"] = ui.input("Pasta Digitalizada", value=str(item.get("link", "") if item else "")).props("outlined dense")
            with ui.row().classes("w-full justify-between mt-4"):
                if item:
                    ui.button("Excluir", icon="delete", color="negative", on_click=confirm_delete).props("outline")
                else:
                    ui.element("div")
                with ui.row().classes("gap-2"):
                    ui.button("Cancelar", on_click=close_dialog).props("flat")
                    ui.button("Salvar", icon="save", color="primary", on_click=save_form)
        dialog.open()

    def handle_double_click(event: Any) -> None:
        args = event.args
        row = None
        if isinstance(args, dict):
            row = args.get("row") or args
        elif isinstance(args, list):
            for value in args:
                if isinstance(value, dict) and ("id" in value or "row" in value):
                    row = value.get("row", value)
                    break
        if row and row.get("id") is not None:
            item = next((value for value in item_table.rows if value["id"] == row["id"]), None)
            if item:
                open_form(item)

    ui.add_head_html("""
        <style>
            body { background: #f5f7fb; }
            .q-table th { font-weight: 700; background: #f0e9df; }
            .q-table tbody tr { cursor: pointer; }
            .q-table tbody tr:hover { background: #fff7ed !important; }
        </style>
    """)

    with ui.header().classes("items-center justify-between bg-amber-950 px-6"):
        with ui.row().classes("items-center gap-3"):
            ui.icon("handshake", size="32px").classes("text-amber-200")
            ui.label("Convênios e Parcerias").classes("text-h5 text-white font-bold")
        ui.label("Cadastro de instrumentos administrativos").classes("text-amber-100")

    with ui.column().classes("w-full max-w-screen-2xl mx-auto p-6 gap-4"):
        with ui.card().classes("w-full"):
            with ui.row().classes("w-full items-end gap-3"):
                search_input = ui.input("Buscar por pasta, nome, conteúdo ou link").props("outlined clearable").classes("flex-1")
                ui.button("Buscar", icon="search", on_click=refresh_table).classes("h-14")
                ui.button("Adicionar registro", icon="add", color="primary", on_click=lambda: open_form()).classes("h-14")
            search_input.on("keydown.enter", refresh_table)

        with ui.row().classes("w-full items-center justify-between"):
            total_label = ui.label()
            ui.label("Dica: dê duplo clique em uma linha para editar ou excluir.").classes("text-gray-600")

        item_table = ui.table(columns=COLUMNS, rows=list_items(), row_key="id", pagination={"rowsPerPage": 25}).classes("w-full")
        item_table.add_slot(
            "body-cell-link",
            """
            <q-td :props="props">
                <a v-if="props.value" :href="props.value" target="_blank" rel="noopener" class="text-amber-800 underline">Abrir pasta</a>
                <span v-else class="text-gray-400">Sem link</span>
            </q-td>
            """,
        )
        item_table.on("rowDblclick", handle_double_click)
        total_label.set_text(f"{len(item_table.rows)} registro(s) exibido(s)")
