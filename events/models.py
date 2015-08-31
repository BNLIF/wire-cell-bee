from django.db import models
from django.conf import settings
import convention
import os, json
from glob import glob

# Create your models here.

class EventSet(models.Model):
    event_type  = models.CharField(max_length=50)
    num_events  = models.IntegerField()
    energy      = models.CharField(max_length=50)
    geometry    = models.CharField(max_length=50)
    desc        = models.CharField(max_length=200, blank=True)
    alias       = models.CharField(max_length=100, blank=True)
    created_at  = models.DateTimeField('date created')

    def __unicode__(self):
        return u'%i: %s @ %s' % (self.pk, self.event_type, self.alias)

    def data_dir(self):
        d = None
        if (self.pk==None):  # temporay, not saved to database
            d = settings.MEDIA_ROOT + self.alias + '/data'
        else:
            d = "%s/%s/%s/data" % (settings.BASE_DIR, settings.DATA_DIR, self.alias)

        if os.path.exists(d):
            return d
        else:
            return None

    def event_list(self):
        results = []
        d = self.data_dir()
        if d:
            results = [ int(x)
                for x in os.listdir(self.data_dir())
                if x.isdigit()
            ]
        return results

    def event_count(self):
        if (self.num_events>0):
            return self.num_events
        else:
            return len(self.event_list())

    def data_info(self, eventNo=0):
        results = {}
        for x in glob('%s/%i/*.json' % (self.data_dir(), eventNo)):
            f = os.path.basename(x).rstrip('.json')
            results[ f[f.find('-')+1:] ] = x
        return results

    def recon_list(self, eventNo=0):
        results = []
        info = self.data_info(eventNo)
        info.pop('mc', None)
        for name in convention.SORTED_RECON_FILES:
            if (name in info):
                results.append(convention.FILENAME_ALIAS.get(name, name))
                info.pop(name, None)
        for name in info.keys():
            results.append(name)
        return results

    def has_MC(self, eventNo=0):
        return 'mc' in self.data_info(eventNo)

    def content_list(self, eventNo=0):
        results = []
        if self.has_MC():
            results.append('mc')
        results.extend(self.recon_list(eventNo))
        return results

    def summary(self):
        info = {}
        d = self.data_dir()
        if not d:
            return info
        summary_file = self.data_dir() + '/summary.json'
        if os.path.exists(summary_file):
            print summary_file, ' found'
            # print self.event_list()
            with open(summary_file) as json_file:
                info = json.load(json_file)
        else:
            if not self.pk>0: # only for tmp dirs
                print 'creating summary: ', summary_file
                for event_id in self.event_list():
                    runNo = 0
                    subRunNo = 0
                    evenNo = 0
                    data_info = self.data_info(event_id)
                    if data_info:
                        with open(data_info.values()[0]) as f:
                            content = json.load(f)
                            runNo = content.get('runNo', 0)
                            subRunNo = content.get('subRunNo', 0)
                            eventNo = content.get('eventNo', 0)
                    info[event_id] = {
                        'runNo': runNo,
                        'subRunNo': subRunNo,
                        'eventNo': eventNo,
                        'content_list': self.content_list(event_id),
                        'data': data_info
                    }
                    with open(summary_file, 'w') as of:
                        json.dump(info, of)
        return info

class UploadFile(models.Model):
    file = models.FileField(upload_to='raw/%Y/%m/%d')
