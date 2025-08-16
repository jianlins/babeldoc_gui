# hook-tiktoken-o200k.py
def register_o200k_base_encoding():
    try:
        import tiktoken
        try:
            import tiktoken_ext.openai_public  # ensure plugin gets loaded
        except Exception:
            pass

        try:
            tiktoken.get_encoding("o200k_base")
            print("[rthook] o200k_base already available")
            return
        except KeyError:
            pass

        try:
            cl100k = tiktoken.get_encoding("cl100k_base")
            if hasattr(tiktoken, "register_encoding"):
                tiktoken.register_encoding("o200k_base", cl100k)
                print("[rthook] registered o200k_base via register_encoding")
                return
        except Exception:
            pass

        try:
            registry = getattr(tiktoken, "registry", None)
            reg = getattr(registry, "_registry", None) if registry else None
            if reg and hasattr(reg, "__setitem__"):
                reg["o200k_base"] = reg.get("cl100k_base") or reg.get("cl100k")
                print("[rthook] patched registry for o200k_base")
                return
        except Exception:
            pass

        print("[rthook] failed to make o200k_base available")
    except Exception as e:
        print(f"[rthook] exception in tiktoken hook: {e}")

register_o200k_base_encoding()
