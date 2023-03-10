import language_tool_python as ltp
lt = ltp.LanguageToolPublicAPI('en-US')
# with ltp.LanguageTool('en-US') as lt:
text = 'A sentence with a error in the Hitchhiker’s Guide tot he Galaxy'
matches = lt.check(text)
print(lt.correct(text))
print(matches)

    

        




