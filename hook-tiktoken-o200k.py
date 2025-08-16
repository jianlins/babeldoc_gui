# PyInstaller runtime hook to register o200k_base encoding for tiktoken

def register_o200k_base_encoding():
    try:
        import tiktoken
        try:
            tiktoken.get_encoding("o200k_base")
        except KeyError:
            try:
                cl100k = tiktoken.get_encoding("cl100k_base")
                if hasattr(tiktoken, "register_encoding"):
                    tiktoken.register_encoding("o200k_base", cl100k)
                else:
                    registry = getattr(tiktoken, "registry", None)
                    reg = getattr(registry, "_registry", None) if registry else None
                    if reg and hasattr(reg, "__setitem__"):
                        reg["o200k_base"] = reg["cl100k_base"]
            except Exception:
                pass
    except Exception:
        pass

register_o200k_base_encoding()
