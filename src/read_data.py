import csv
from pathlib import Path


def load_all(folder):
    esims = []
    for path in sorted(Path(folder).glob('*.csv')):
        file_esims = []
        try:
            with open(path, encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                for data in reader:
                    sku = data[0]
                    provider = data[1]
                    country = data[4]
                    if data[5] == "":
                        data_gb = None
                    else:
                        data_gb = float(data[5])
                    validity = int(data[7])
                    price = float(data[8])
                    network = data[10]
                    top_up = data[11]
                    file_esims.append([sku, provider, country, data_gb, validity, price, network, top_up])
        except StopIteration:
            print("Warning:", path.name, "is empty, file skipped.")
        except (IndexError, ValueError):
            print("Warning:", path.name, "contains invalid data, file skipped.")
        else:
            if not file_esims:
                print("Warning:", path.name, "has no products, file skipped.")
            esims.extend(file_esims)
    return esims
