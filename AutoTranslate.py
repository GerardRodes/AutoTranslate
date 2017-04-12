# -*- coding: utf-8 -*-

import os
import json
import requests
import urllib


def dump(data):
  print json.dumps(data, indent=2)


class AutoTranslate(object):
  
  API_KEYS = ['trnsl.1.1.20170407T184318Z.5757969e5f9ce34d.f8c9bed978c7d2dfd59bebe4fd6bea92f0a05cc9',
              'trnsl.1.1.20170411T115549Z.0f958e65e97f0a7f.614338348957347456037644c2cc30b928e31658',
              'trnsl.1.1.20170411T115943Z.cfea43dbbcd66f79.1899e548da3d1d0b46f3e2f51aa1dc15d6110026']
  YANDEX_URL = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
  
  def __init__(self, domain, source_language='en', locales_path = '.', overwrite = False):
    self.domain = domain
    self.source_language = source_language
    self.locales_path = locales_path
    self.overwrite = overwrite
    
    self.files = []
    
    
  def __call__(self):
    self.parse_files()
    self.translate_files()
    self.rebuild_files()
  
  
  @property
  def languages(self):
    return [f for f in os.listdir(self.locales_path) if os.path.isdir(os.path.join(self.locales_path, f)) and len(f) == 2]
    
  
  def parse_files(self):
    for language in self.languages:
      file_info = {
        'language' : language,
        'file_path': '/'.join( (self.locales_path, language, 'LC_MESSAGES', self.domain + '.po') ),
        'lines': [],
        'translations': []
      }
      
      with open(file_info['file_path'], 'rU') as file:
        file_info['lines'] = [line for line in file.readlines()]
        
        for i, line in enumerate(file_info['lines']):
          
          if line.startswith('msgid'):
            msgid = line.strip('\n')[7:-1]
            next_line = file_info['lines'][i+1]
            
            if msgid and next_line.startswith('msgstr'):
              msgstr = next_line.strip('\n')[8:-1]
              if not msgstr or self.overwrite:
                file_info['translations'].append({
                    'msgid' : msgid,
                    'msgstr': msgstr,
                    'line'  : i+1,
                  })
      
      self.files.append(file_info)


      
      
  def translate_files(self):
    api_key = 0
    
    for file in self.files:
      print 'translating to ' + file['language']
      if file['translations']:
        lang_direction = 'en-' + file['language']
        data = {
          'key' : self.API_KEYS[api_key],
          'lang': lang_direction,
          'text': '',
        }

        for i, translation in enumerate(file['translations']):
          success = False
          while not success:
            data['text'] = translation['msgid']
            r = requests.post(self.YANDEX_URL, data=data)
            response = r.json()

            translation['msgstr'] = response['text'][0]

            if response['code'] == 200:
              success = True
            elif response['code'] in [401, 402, 404]:
              print 'api key error: ' + str(response['code'])
              if api_key < len(self.API_KEYS):
                api_key += 1
                data['key'] = self.API_KEYS[api_key]
              else:
                print 'no api keys left.'
                success = True
            else:
              print 'error: ' + str(response['code'])
              success = True

          print 'translated %i/%i' % (i+1, len(file['translations']))

      else:
        print 'nothing no translate, if you want to overwrite existing translation set overwrite parameter to True'



  def rebuild_files(self):
    for file in self.files:
      modified_file = file['lines']

      if file['translations']:
        for translation in file['translations']:
          line_to_edit = int(translation['line'])
          new_line_str = 'msgstr "%s"\n' % translation['msgstr']

          modified_file[line_to_edit] = new_line_str

        
        new_file_path = '/'.join( (self.locales_path, file['language'], 'LC_MESSAGES', self.domain + '.new.po') )

        with open(new_file_path, 'w') as new_file:
          new_file.write( u''.join(modified_file).encode('utf-8') )

        if os.path.exists(new_file_path):
          os.remove(file['file_path'])
          os.rename(new_file_path, file['file_path'])

            
        
        
        
        
      
at = AutoTranslate(domain='product.incidences')
at()