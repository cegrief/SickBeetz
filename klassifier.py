### Experimenting with KNN for n-dimensional arrays

from sklearn.metrics import classification_report, confusion_matrix
from sklearn.neighbors import KNeighborsClassifier
import librosa


def train_classifier(data, labels):
    model = KNeighborsClassifier()
    model.fit(data, labels)

    expected = labels
    predicted = model.predict(data)

    print classification_report(expected, predicted)
    print confusion_matrix(expected, predicted)

    return model


def use_classifier(classifier, sample):
    p = classifier.predict(sample)
    print "Sample: %s\nPrediction: %s" % (sample, p)
    return


def main():
    data = []
    labels = []
    dataset = open('training/dataset1.txt', 'r')
    for line in dataset:
        line.split(',')
        data.append(list(line[0]))
        labels += line[2]
    # print data, labels
    m = train_classifier(data, labels)
    use_classifier(m, 3.5)
    return


if __name__ == "__main__":
    main()