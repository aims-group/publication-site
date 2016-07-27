import pymysql
from datetime import datetime
import urllib
from publisher.models import *
from django.contrib.auth.models import User
from local_settings import *


def main():
    db = pymysql.connect(host=host, user=user, passwd=password, db=database)

    publication_list = db.cursor()
    publication_list.execute("SELECT publication_id FROM publication;")

    for row in publication_list.fetchall():
        current_id = row[0]
        pub_type = 'J'
        print current_id

        # NEW PUB #
        new_publication = Publication()
        # END NEW PUB #

        # NOT USED in old Database #
        #    new_publication.projects
        #    new_publication.project_number
        #    new_publication.task_number
        #    new_publication.abstract
        # END NOT USED #

        # SUBMITTER #
        new_publication.submitter = User.objects.filter(id=1)[0]
        # END SUBMITTER #

        # TITLE #
        publication_title = db.cursor()
        publication_title.execute("SELECT a.attribute_value FROM attribute AS a JOIN publication_has_attribute AS pha WHERE pha.attribute_id = a.attribute_id AND a.attribute_key = 'title' AND publication_id = " + str(current_id))
        for title in publication_title.fetchall():
            new_publication.title = urllib.unquote(title[0]).decode("latin1").encode("UTF8")
            # print new_publication.title
        # END TITLE #

        # STATUS #
        publication_status = db.cursor()
        old_status = "Not Applicable"  # if old publication did not have a status I'm setting it to not applicable
        publication_status.execute("SELECT a.attribute_value FROM attribute AS a JOIN publication_has_attribute AS pha WHERE pha.attribute_id = a.attribute_id AND a.attribute_key = 'jstatus' AND publication_id = " + str(current_id))
        for status in publication_status.fetchall():
            old_status = status[0]
        for status_choice in PUBLICATION_STATUS_CHOICE:
            if old_status.capitalize() == status_choice[1].capitalize():
                new_publication.status = status_choice[0]
        publication_status.close()
        # END STATUS #

        # DOI #
        publication_doi = db.cursor()
        publication_doi.execute("SELECT a.attribute_value FROM attribute AS a JOIN publication_has_attribute AS pha WHERE pha.attribute_id = a.attribute_id AND attribute_key = 'doi' AND publication_id = " + str(current_id))
        for doi in publication_doi.fetchall():
            new_publication.doi = doi[0].decode("latin1").encode("UTF8")
            # print new_publication.doi
        publication_doi.close()
        # END DOI #

        # TYPE #
        publication_type = db.cursor()
        publication_type.execute("SELECT publication_type FROM publication where publication_id = " + str(current_id))
        for ptype in publication_type.fetchall():
            pub_type = ptype[0]
        publication_type.close()
        if pub_type == 'J':
            new_publication.publication_type = 2
        elif pub_type == 'A' or pub_type == 'P':
            new_publication.publication_type = 1
        elif pub_type == 'T':
            new_publication.publication_type = 6
        else:
            new_publication.publication_type = 7
        # END TYPE #

        # URL #
        publication_url = db.cursor()
        publication_url.execute("SELECT article_url FROM publication WHERE publication_id = " + str(current_id))
        for url in publication_url.fetchall():
            new_publication.url = url[0].decode("latin1").encode("UTF8")
            # print new_publication.url
        publication_url.close()
        # END URL #

        # DATE #
        publication_date = db.cursor()
        publication_date.execute("SELECT publication_year FROM publication WHERE publication_id = " + str(current_id))
        for year in publication_date:
            new_publication.publication_date = datetime.strptime("1/1/" + str(year[0]), '%m/%d/%Y')
            # print new_publication.publication_date
            if not AvailableYears.objects.filter(year=year[0]):
                print year[0]
                new_year = AvailableYears()
                new_year.year = year[0]
                new_year.save()
        publication_date.close()
        # END DATE #

        # SAVE #
        new_publication.save()
        # END SAVE #

        # PROJECT #
        new_publication.projects.add(Project.objects.filter(id=1)[0])
        # END PROJECT #

        # FUNDING #
        publication_funding = db.cursor()
        publication_funding.execute("SELECT * from publication where publication_id = " + str(current_id))
        for funding in publication_funding:
            pub_funding = Funding()
            pub_funding.funding = funding[0]
            pub_funding.save()
            new_publication.funding.add(pub_funding)
        publication_funding.close()
        # END FUNDING #

        # TYPE #
        if pub_type == 'J':
            new_journal = Journal()
            new_journal.publication_id = new_publication
            # Journal Name
            new_journal.journal_name = JournalOptions.objects.filter(journal_name='Other')[0]
            journal_name = db.cursor()
            journal_name.execute("SELECT a.attribute_value FROM publication as p, attribute as a, publication_has_attribute as pa where p.publication_id = pa.publication_id and a.attribute_id = pa.attribute_id AND attribute_key = 'journal' AND p.publication_id = " + str(current_id))
            for name in journal_name.fetchall():
                if JournalOptions.objects.filter(journal_name=name[0]):
                    new_journal.journal_name = JournalOptions.objects.filter(journal_name=name[0])[0]
                else:
                    new_journal.journal_name = JournalOptions.objects.filter(journal_name='Other')[0]
                    print str(current_id) + " -- FAIL -- JOURNAL NAME"
            journal_name.close()
            # Volume Number
            journal_vn = db.cursor()
            journal_vn.execute("SELECT a.attribute_value FROM publication as p, attribute as a, publication_has_attribute as pa where p.publication_id = pa.publication_id and a.attribute_id = pa.attribute_id AND attribute_key = 'volume' AND p.publication_id = " + str(current_id))
            for vn in journal_vn.fetchall():
                new_journal.volume_number = vn[0].decode("latin1").encode("UTF8")
            journal_vn.close()
            # Article Number
            journal_an = db.cursor()
            journal_an.execute("SELECT a.attribute_value FROM publication as p, attribute as a, publication_has_attribute as pa where p.publication_id = pa.publication_id and a.attribute_id = pa.attribute_id AND display_name = 'Artilce Nubmer' AND p.publication_id = " + str(current_id))
            for an in journal_an.fetchall():
                new_journal.article_number = an[0].decode("latin1").encode("UTF8")
            journal_an.close()
            # Start Page
            journal_sp = db.cursor()
            journal_sp.execute("SELECT a.attribute_value FROM publication as p, attribute as a, publication_has_attribute as pa where p.publication_id = pa.publication_id and a.attribute_id = pa.attribute_id AND attribute_key = 'pg_start' AND p.publication_id = " + str(current_id))
            for sp in journal_sp.fetchall():
                new_journal.start_page = sp[0].decode("latin1").encode("UTF8")
            journal_sp.close()
            # End Page
            journal_ep = db.cursor()
            journal_ep.execute("SELECT a.attribute_value FROM publication as p, attribute as a, publication_has_attribute as pa where p.publication_id = pa.publication_id and a.attribute_id = pa.attribute_id AND attribute_key = 'pg_end' AND p.publication_id = " + str(current_id))
            for ep in journal_ep.fetchall():
                new_journal.end_page = ep[0].decode("latin1").encode("UTF8")
            journal_ep.close()
            # Save
            new_journal.save()

        elif pub_type == 'A' or pub_type == 'P':
            new_conference = Conference()
            # publication_id
            new_conference.publication_id = new_publication
            # conference_name
            conference_name = db.cursor()
            conference_name.execute("SELECT a.attribute_value FROM publication as p, attribute as a, publication_has_attribute as pa where p.publication_id = pa.publication_id and a.attribute_id = pa.attribute_id AND a.attribute_key = 'conf' AND p.publication_id = " + str(current_id))
            for con_name in conference_name.fetchall():
                if con_name[0] == 'Other':
                    conference_other_name = db.cursor()
                    conference_other_name.execute("SELECT a.attribute_value FROM publication as p, attribute as a, publication_has_attribute as pa where p.publication_id = pa.publication_id and a.attribute_id = pa.attribute_id AND a.attribute_key = 'otherConference' AND p.publication_id = " + str(current_id))
                    for con_on in conference_other_name.fetchall():
                        new_conference.conference_name = con_on[0].decode("latin1").encode("UTF8")
                else:
                    new_conference.conference_name = con_name[0].decode("latin1").encode("UTF8")
            conference_name.close()
            # conference_serial_number
            conference_sn = db.cursor()
            conference_sn.execute("SELECT a.attribute_value FROM publication as p, attribute as a, publication_has_attribute as pa where p.publication_id = pa.publication_id and a.attribute_id = pa.attribute_id AND a.attribute_key = 'confserial' AND p.publication_id = " + str(current_id))
            for con_sn in conference_sn.fetchall():
                new_conference.conference_serial_number = con_sn[0].decode("latin1").encode("UTF8")
            conference_sn.close()
            # event_location
            conference_location = db.cursor()
            conference_location.execute("SELECT a.attribute_value FROM publication as p, attribute as a, publication_has_attribute as pa where p.publication_id = pa.publication_id and a.attribute_id = pa.attribute_id AND a.attribute_key = 'confcity' AND p.publication_id = " + str(current_id))
            for con_loc in conference_location.fetchall():
                new_conference.event_location = con_loc[0].decode("latin1").encode("UTF8")
            conference_location.close()
            # start_page
            conference_sp = db.cursor()
            conference_sp.execute("SELECT a.attribute_value FROM publication as p, attribute as a, publication_has_attribute as pa where p.publication_id = pa.publication_id and a.attribute_id = pa.attribute_id AND a.attribute_key = 'pg_start' AND p.publication_id = " + str(current_id))
            for con_sp in conference_sp.fetchall():
                new_conference.start_page = con_sp[0].decode("latin1").encode("UTF8")
            conference_sp.close()
            # end_page
            conference_ep = db.cursor()
            conference_ep.execute("SELECT a.attribute_value FROM publication as p, attribute as a, publication_has_attribute as pa where p.publication_id = pa.publication_id and a.attribute_id = pa.attribute_id AND a.attribute_key = 'pg_end' AND p.publication_id = " + str(current_id))
            for con_ep in conference_ep.fetchall():
                new_conference.end_page = con_ep[0].decode("latin1").encode("UTF8")
            conference_ep.close()
            # editor
            conference_editor = db.cursor()
            conference_editor.execute("SELECT a.attribute_value FROM publication as p, attribute as a, publication_has_attribute as pa where p.publication_id = pa.publication_id and a.attribute_id = pa.attribute_id AND a.attribute_key = 'editor' AND p.publication_id = " + str(current_id))
            for con_edit in conference_editor.fetchall():
                new_conference.editor = con_edit[0].decode("latin1").encode("UTF8")
            conference_editor.close()
            # city_of_publication
            conference_cop = db.cursor()
            conference_cop.execute("SELECT a.attribute_value FROM publication as p, attribute as a, publication_has_attribute as pa where p.publication_id = pa.publication_id and a.attribute_id = pa.attribute_id AND a.attribute_key = 'pubcity' AND p.publication_id = " + str(current_id))
            for con_cop in conference_cop.fetchall():
                new_conference.city_of_publication = con_cop[0].decode("latin1").encode("UTF8")
            conference_cop.close()
            # publisher
            conference_pub = db.cursor()
            conference_pub.execute("SELECT a.attribute_value FROM publication as p, attribute as a, publication_has_attribute as pa where p.publication_id = pa.publication_id and a.attribute_id = pa.attribute_id AND a.attribute_key = 'publisher' AND p.publication_id = " + str(current_id))
            for con_pub in conference_pub.fetchall():
                new_conference.publisher = con_pub[0].decode("latin1").encode("UTF8")
            conference_pub.close()
            new_conference.save()

        elif pub_type == 'T':
            new_technical_report = TechnicalReport()
            # publication_id
            new_technical_report.publication_id = new_publication
            # report_number
            report_number = db.cursor()
            report_number.execute("SELECT a.attribute_value FROM publication as p, attribute as a, publication_has_attribute as pa where p.publication_id = pa.publication_id and a.attribute_id = pa.attribute_id AND a.attribute_key = 'reportnum' AND p.publication_id = " + str(current_id))
            for rn in report_number.fetchall():
                new_technical_report.report_number = rn[0]
            report_number.close()
            # editor
            report_editor = db.cursor()
            report_editor.execute("SELECT a.attribute_value FROM publication as p, attribute as a, publication_has_attribute as pa where p.publication_id = pa.publication_id and a.attribute_id = pa.attribute_id AND a.attribute_key = 'editor' AND p.publication_id = " + str(current_id))
            for re in report_editor.fetchall():
                new_technical_report.editor = re[0]
            report_editor.close()
            # issuer
            report_issuer = db.cursor()
            report_issuer.execute("SELECT a.attribute_value FROM publication as p, attribute as a, publication_has_attribute as pa where p.publication_id = pa.publication_id and a.attribute_id = pa.attribute_id AND a.attribute_key = 'issuer' AND p.publication_id = " + str(current_id))
            for ri in report_issuer.fetchall():
                new_technical_report.issuer = ri[0]
            report_issuer.close()
            new_technical_report.save()
        else:
            new_other = Other()
            # publication_id
            new_other.publication_id = new_publication
            # other_pub
            other_publication = db.cursor()
            other_publication.execute("SELECT a.attribute_value FROM publication as p, attribute as a, publication_has_attribute as pa where p.publication_id = pa.publication_id and a.attribute_id = pa.attribute_id AND a.attribute_key = 'reportnum' AND p.publication_id = " + str(current_id))
            for op in other_publication.fetchall():
                new_other.other_pub = op[0]
            other_publication.close()
            new_other.save()
        # END TYPE #

        # AUTHORS #
        publication_authors = db.cursor()
        publication_authors.execute(
            "SELECT a.last_name, a.first_name, a.middle_initial FROM publication as p, author as a, publication_has_author as pa where p.publication_id = pa.publication_id and a.author_id = pa.author_id AND p.publication_id = " + str(current_id))
        for author in publication_authors.fetchall():
            author_holder = author[0].decode("latin1").encode("UTF8")
            if author[1]:
                author_holder += " " + author[1][:1].decode("latin1").encode("UTF8") + "."
            if author[2]:
                author_holder += " " + author[2][:1].decode("latin1").encode("UTF8") + "."
            # print author_holder
            new_author = Author()
            new_author.name = author_holder
            new_author.save()
            new_publication.authors.add(new_author.id)
        publication_authors.close()
        # END AUTHORS #

        # MODEL #
        publication_model = db.cursor()
        publication_model.execute("SELECT attribute.display_name FROM publication, publication_has_attribute, attribute WHERE attribute.attribute_key = 'model' and publication.publication_id = publication_has_attribute.publication_id and publication_has_attribute.attribute_id= attribute.attribute_id and publication.publication_id = " + str(current_id))
        for pub_model in publication_model.fetchall():
            if Model.objects.filter(model=pub_model[0]):
                #new_publication.model.add(Model.objects.filter(model=pub_model[0])[0])
                new_pubmodel = PubModels()
                new_pubmodel.publication = new_publication
                new_pubmodel.model = Model.objects.filter(model=pub_model[0])[0]
                new_pubmodel.ensemble = 1
                new_pubmodel.save()

                # print Model.objects.filter(model=pub_model[0])[0]
            else:
                print pub_model[0] + " -- FAIL -- MODEL"
        publication_model.close()
        # END MODEL #

        # KEYWORD #
        publication_keyword = db.cursor()
        publication_keyword.execute("SELECT attribute.display_name FROM publication, publication_has_attribute, attribute WHERE attribute.attribute_key = 'keyword' and publication.publication_id = publication_has_attribute.publication_id and publication_has_attribute.attribute_id= attribute.attribute_id and publication.publication_id = " + str(current_id))
        for pub_key in publication_keyword.fetchall():
            if Keyword.objects.filter(keyword=pub_key[0]):
                new_publication.keywords.add(Keyword.objects.filter(keyword=pub_key[0])[0])
                # print Keyword.objects.filter(keyword=pub_key[0])[0]
            else:
                print pub_key[0] + " -- FAIL -- KEYWORD"
        publication_keyword.close()
        # END KEYWORD #

        # VARIABLE #
        publication_variable = db.cursor()
        publication_variable.execute("SELECT attribute.display_name FROM publication, publication_has_attribute, attribute WHERE attribute.attribute_key = 'variable' and publication.publication_id = publication_has_attribute.publication_id and publication_has_attribute.attribute_id= attribute.attribute_id and publication.publication_id = " + str(current_id))
        for pub_var in publication_variable.fetchall():
            if Variable.objects.filter(variable=pub_var[0]):
                new_publication.variables.add(Variable.objects.filter(variable=pub_var[0])[0])
                #print Variable.objects.filter(variable=pub_var[0])[0]
            else:
                print pub_var[0] + " -- FAIL -- VARIABLE"
        publication_variable.close()
        # END VARIABLE #

        # EXPERIMENT #
        publication_experiment = db.cursor()
        publication_experiment.execute("SELECT attribute.display_name FROM publication, publication_has_attribute, attribute WHERE attribute.attribute_key = 'experiment' and publication.publication_id = publication_has_attribute.publication_id and publication_has_attribute.attribute_id= attribute.attribute_id and publication.publication_id = " + str(current_id))
        for pub_exp in publication_experiment.fetchall():
            if Experiment.objects.filter(experiment=pub_exp[0]):
                new_publication.experiments.add(Experiment.objects.filter(experiment=pub_exp[0])[0])
                # print Experiment.objects.filter(experiment=pub_exp[0])[0]
            else:
                print pub_exp[0] + " -- FAIL -- EXPERIMENT"
        publication_experiment.close()
        # END EXPERIMENT #

        # FREQUENCY #
        publication_frequency = db.cursor()
        publication_frequency.execute("SELECT attribute.display_name FROM publication, publication_has_attribute, attribute WHERE attribute.attribute_key = 'frequency' and publication.publication_id = publication_has_attribute.publication_id and publication_has_attribute.attribute_id= attribute.attribute_id and publication.publication_id = " + str(current_id))
        for pub_freq in publication_frequency.fetchall():
            if Frequency.objects.filter(frequency=pub_freq[0]):
                new_publication.frequency.add(Frequency.objects.filter(frequency=pub_freq[0])[0])
                # print Frequency.objects.filter(frequency=pub_freq[0])[0]
            else:
                print pub_freq[0] + " -- FAIL FREQUENCY"
        publication_frequency.close()
        # END FREQUENCY #

    publication_list.close()
